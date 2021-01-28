import json
import os
import requests
from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


# Stockholm by default
def get_pop_valid_interval(pop_name='bma', workers=1, start_at=1, end_at=1000, save_reaching_errors=False):
	FASTLY_TOKEN=os.environ.get("FASTLY_API_TOKEN", None)
	OUT_FOLDER=os.environ.get("OUT_FOLDER", "out")
	SERVICE_ADDRESS=os.environ.get("SERVICE_ADDRESS", None)	
	HIT_TIMEOUT=os.environ.get("TIMEOUT", 10)
	RETRY=os.environ.get("RETRY_COUNT", 1)

	if FASTLY_TOKEN is None:
		raise Exception("You should provide the FASTLY_API_TOKEN environment variable")

	if SERVICE_ADDRESS is None:
		raise Exception("You should provide the SERVICE_ADDRESS environment variable")
	retries = Retry(total=RETRY, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
	
	adapter = HTTPAdapter(max_retries=retries)
	http = requests.Session()

	result_dict = dict(pop_name=pop_name, range=[start_at, end_at],
		valid=[],
		info=[],
		redirects=[],
		client_error=[],
		server_error=[],
		reach_error=[]
	)
	for at in range(start_at, end_at + 1):
		try:
			http.mount("https://", adapter)

			print(f"Hitting {pop_name} at {at}")
			#pops_request = requests.get(, , timeout=HIT_TIMEOUT, max_retries=retries )

			result = http.get(f"https://cache-{pop_name}{at}.hosts.secretcdn.net",headers = {
				"X-Pass": "1",
				"X-Origin": "https_teamc_origin",
				"Host": SERVICE_ADDRESS
			},timeout=HIT_TIMEOUT, verify=False)
			
			status_code = result.status_code
			response_body = result.content

			print(response_body, status_code)

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
			result_dict[classification].append(dict(at=at, 
			headers=headers,
			response=response_body.decode()))

		except KeyboardInterrupt as e:
			break
		except Exception as e:
			if save_reaching_errors:
				result_dict["reach_error"].append(dict(at=at, response=f"{e}"))
			continue

		#if status_code >= 400 and status_code < 500:
		#	raise Exception(f"Bad request error {json_result}")

	open(f"{OUT_FOLDER}/range_{pop_name}.json", 'w').write(json.dumps(result_dict))

	return result

if __name__ == "__main__":
	get_pop_valid_interval(pop_name="sea", start_at=4470, end_at=4470, save_reaching_errors=False)
