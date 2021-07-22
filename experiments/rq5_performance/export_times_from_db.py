from utils.dbutils import DBUtils
import os
import sys
import json

DB=DBUtils(passwd=os.environ.get("MONGO_PASS"), usr=os.environ.get("MONGO_USER"))

if __name__ == "__main__":
    fn = sys.argv[1]
    to = sys.argv[2]

    timesO = DB.get_times(name=fn, tpe="original", session="inlined")
    timesI = DB.get_times(casename=fn, tpe="instrumented", session="inlined")

    if not timesI:
        raise Exception(fn)

    r = {
        fn: dict(
            original=dict(
                times=[t for t in timesO if t != -1]
            ),
            pureRandom=dict(
                times=[t for t in timesI if t != -1]
            )
        )
    }

    open(to, 'w').write(json.dumps(r))