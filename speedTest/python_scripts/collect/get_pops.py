import json
import os
import requests

from common.common import *

def get_pops():
	FASTLY_TOKEN=os.environ.get("FASTLY_API_TOKEN", None)
	OUT_FOLDER=os.environ.get("OUT_FOLDER", "out")

	if FASTLY_TOKEN is None:
		raise Exception("You should provide the FASTLY_API_TOKEN environment variable")

	pops_request = requests.get(f"https://api.fastly.com/datacenters", headers = {
		"Fastly-Key": FASTLY_TOKEN
	})
	json_result = pops_request.json()
	status_code = pops_request.status_code

	if status_code >= 400 and status_code < 500:
		raise Exception(f"Bad request error {json_result}")

	if status_code == 200:
		open(f"{OUT_FOLDER}/pops.json", 'w').write(json.dumps(json_result))

	return json_result

if __name__ == "__main__":
	get_pops()
