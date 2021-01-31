import os
from requests.packages.urllib3.util.retry import Retry


FASTLY_TOKEN=os.environ.get("FASTLY_API_TOKEN", None)
OUT_FOLDER=os.environ.get("OUT_FOLDER", "out")
SERVICE_ADDRESS=os.environ.get("SERVICE_ADDRESS", None)	
HIT_TIMEOUT=os.environ.get("TIMEOUT", 1)
RES_TIMEOUT=os.environ.get("RES_TIMEOUT", 3)
RETRY=os.environ.get("RETRY_COUNT", 1)
retries = Retry(total=RETRY, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])