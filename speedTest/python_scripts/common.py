import os
from requests.packages.urllib3.util.retry import Retry


FASTLY_TOKEN=os.environ.get("FASTLY_API_TOKEN", None)
OUT_FOLDER=os.environ.get("OUT_FOLDER", "out")
SERVICE_ADDRESS=os.environ.get("SERVICE_ADDRESS", None)	
HIT_TIMEOUT=int(os.environ.get("TIMEOUT", 1))
RES_TIMEOUT=int(os.environ.get("RES_TIMEOUT", 3))
RETRY=int(os.environ.get("RETRY_COUNT", 1))
PRINT_LATEX=bool(os.environ.get("PRINT_LATEX", False))

PACKAGE_FOLDER=os.environ.get("PACKAGE_FOLDER", None)
DEPLOYMENT_SCRIPT=os.environ.get("DEPLOYMENT_SCRIPT", None)
DEPLOYMENT_SERVICE_ID=os.environ.get("DEPLOYMENT_SERVICE_ID", None)

POP_MACHINE_STRATEGY = int(os.environ.get("POP_MACHINE_STRATEGY", 0)) # 0 means random, 1 for all
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 0.1)) # 10 seconds
DEPLOY_INTERVAL = int(os.environ.get("DEPLOY_INTERVAL", 60)) # 60 seconds, every 1 min


EXCHANGE=os.environ.get("EXCHANGE", "deploy")
EXCHANGE_HOST=os.environ.get("EXCHANGE_HOST", "127.0.0.1")
EXCHANGE_PORT=os.environ.get("EXCHANGE_PORT", 5672)
EXCHANGE_TYPE=os.environ.get("EXCHANGE_TYPE", "topic")
EXCHANGE_PROCESS_ID=os.environ.get("EXCHANGE_PROCESS_ID", "generate.variant")
EXCHANGE_QUEUE=os.environ.get("EXCHANGE_QUEUE", "timing_test")


retries = Retry(total=RETRY, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])

try:
    from common_secret import *
except Exception as e:
    print(e)