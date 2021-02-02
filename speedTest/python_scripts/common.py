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
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", 0.1)) # 10ms seconds
DEPLOY_INTERVAL = int(os.environ.get("DEPLOY_INTERVAL", 600)) # 60 seconds, every 1 min
MAX_TIME = int(os.environ.get("MAX_TIME", 3600)) 
DYNAMICALLY_LOAD_POP_NAMES = bool(os.environ.get("DYNAMICALLY_LOAD_POP_NAMES", True)) 
MAX_THREADS_PER_TIME = int(os.environ.get("MAX_THREADS_PER_TIME", 10)) 


EXCHANGE=os.environ.get("EXCHANGE", "deploy")
EXCHANGE_HOST=os.environ.get("EXCHANGE_HOST", "127.0.0.1")
EXCHANGE_PORT=os.environ.get("EXCHANGE_PORT", 5672)
EXCHANGE_TYPE=os.environ.get("EXCHANGE_TYPE", "topic")
EXCHANGE_PROCESS_ID=os.environ.get("EXCHANGE_PROCESS_ID", "generate.variant")
EXCHANGE_QUEUE=os.environ.get("EXCHANGE_QUEUE", "timing_test")

CREATE_VIDEO_FROM_EVENTS=bool(os.environ.get("CREATE_VIDEO_FROM_EVENTS", False)) 

MONGO_USER=os.environ.get("MONGO_USER", None)
MONGO_PASS=os.environ.get("MONGO_PASS", None)


try:
    from common_secret import *
except Exception as e:
    print(e)

MONGO_DB=os.environ.get("MONGO_DB", "fastly4edge_1h2")
MONGO_URI=os.environ.get("MONGO_URI", f"mongodb://{MONGO_USER}:{MONGO_PASS}@127.0.0.1:27017/{MONGO_DB}?authSource=admin")


retries = Retry(total=RETRY, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
