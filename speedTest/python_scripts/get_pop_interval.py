import json
import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED
import  sys

FASTLY_TOKEN=os.environ.get("FASTLY_API_TOKEN", None)
OUT_FOLDER=os.environ.get("OUT_FOLDER", "out")
SERVICE_ADDRESS=os.environ.get("SERVICE_ADDRESS", None)	
HIT_TIMEOUT=os.environ.get("TIMEOUT", 1)
RES_TIMEOUT=os.environ.get("RES_TIMEOUT", 3)
RETRY=os.environ.get("RETRY_COUNT", 1)
retries = Retry(total=RETRY, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])


STOP=False

def hitpop(pop_name, pop_at, save_reaching_errors):
	global STOP

	if STOP:
		raise Exception("STOPSIGNAL")

	adapter = HTTPAdapter(max_retries=retries)
	http = requests.Session()

	try:
		http.mount("https://", adapter)

		if pop_at  % 100  == 0:
			print(f"Hitting {pop_name} at {pop_at}")
		#pops_request = requests.get(, , timeout=HIT_TIMEOUT, max_retries=retries )

		result = http.get(f"https://cache-{pop_name}{pop_at}.hosts.secretcdn.net",headers = {
			"X-Pass": "1",
			"X-Origin": "https_teamc_origin",
			"Host": SERVICE_ADDRESS
		},timeout=HIT_TIMEOUT, verify=False)
		
		status_code = result.status_code
		response_body = result.content

		print(response_body, status_code, pop_at)

		if status_code >= 100 and status_code < 200:
			classification="info"
		if status_code >= 200 and status_code < 300:
			classification="valid"
		if status_code >= 300 and status_code < 400:
			classification="redirects"
		if status_code >= 400 and status_code < 500:
			classification="client_error"
		if status_code >= 500:
			classification="server_error"
		
		headers = [(k, v) for k, v in result.headers.items()]

		return (classification, dict(at=pop_at, 
		headers=headers,
		response=response_body.decode()))

	except KeyboardInterrupt as e:
		# TODO send interrupt event
		STOP=True
	except Exception as e:
		if save_reaching_errors:
			return ("reach_error", dict(at=pop_at, response=f"{e}"))
		

# Stockholm by default
def get_pop_valid_interval(pop_name='bma', workers=1, start_at=1, end_at=1000, save_reaching_errors=True):
	

	if FASTLY_TOKEN is None:
		raise Exception("You should provide the FASTLY_API_TOKEN environment variable")

	if SERVICE_ADDRESS is None:
		raise Exception("You should provide the SERVICE_ADDRESS environment variable")
	
	
	result_dict = dict(pop_name=pop_name, range=[start_at, end_at],
		valid=[],
		info=[],
		redirects=[],
		client_error=[],
		server_error=[],
		reach_error=[]
	)

	hitPool = ThreadPoolExecutor(max_workers=workers)
	jobs = []
	for at in range(start_at, end_at + 1):
		job = hitPool.submit(hitpop, pop_name, at, save_reaching_errors)
                    
		jobs.append(job)
	done, fail = wait(jobs, return_when=ALL_COMPLETED)
	futures = []

	try:
		for f in done:
			pack = f.result(timeout=RES_TIMEOUT)
			if pack is not None:
				class_, r = pack
				result_dict[class_].append(r)
	except KeyboardInterrupt as e:
		pass
		#if status_code >= 400 and status_code < 500:
		#	raise Exception(f"Bad request error {json_result}")
	# TODO Sort results
	open(f"{OUT_FOLDER}/range_{pop_name}.json", 'w').write(json.dumps(result_dict))

	return result_dict

if __name__ == "__main__":
	pops=["bma", "sea", "vie", "bog"]
	for p in pops:
		get_pop_valid_interval(pop_name=p, start_at=0, end_at=20000, save_reaching_errors=False, workers=50)
