import sys
import os
import string
import shutil
import json
import sys
import gridfs
import pymongo
import redis 

# Redis for memoization

class RedisCache(object):

    def __init__(self, passwd, host="localhost", port=6380) -> None:
        self.cache = redis.Redis(
                host=host,
                port=port,
                password=passwd,
                db=0,
                socket_timeout=60,
                socket_connect_timeout=60,
                retry_on_timeout=True,
            )

    def memoize(self):
        def wrapper(func):
            def _f(*args, **kwargs):
                k = ":".join([a.__str__() for a in args])
                zipped = zip(kwargs.items())
                zipped = ":".join([f"{k}-{v}" for k, v in zipped])
                totalk = f"{k}:{zipped}"
                print(totalk, kwargs)
                r = self.cache.get(totalk)
                if r is not None:
                    return eval(r.decode())
                
                real_result = func(*args, **kwargs)

                self.cache.set(totalk, real_result.__str__().encode())

                return real_result
            return _f
        return wrapper


redis_cache = RedisCache(
    os.environ.get("REDIS_PASS", None),
    host=os.environ.get("REDIS_HOST", "localhost"),
    port=int(os.environ.get("REDIS_PORT", "6380")))




class DBUtils(object):


    def __init__(self, dbname="fastly4edge", connection="localhost:27017", passwd=None, usr=None):
        if usr == None:
            self.client = pymongo.MongoClient(f"mongodb://{connection}/")
        else:
            self.client = pymongo.MongoClient(f"mongodb://{usr}:{passwd}@{connection}/")


        self.db = self.client[dbname]
        self.fs = gridfs.GridFS(self.db)

    def count_paths(self, popname, casename, collection="paths", sessionname="test1", **kwargs):
        return self.db[collection].count_documents(dict(
            pop=popname,
            casename=casename,
            session=sessionname,
            **kwargs
        ))

    def get_paths(self, popname, casename, collection="paths", sessionname="test1", **kwargs):
        for i in self.db[collection].find(dict( pop=popname,
            casename=casename,
            session=sessionname,
            **kwargs
            )):
            yield dict(
                **i,
                pathraw=json.loads(self.fs.get(i['path']).read().decode()) # project the large file
            )
    

    def count_all_paths(self, casename, collection="paths", sessionname="test1", **kwargs):
        return self.db[collection].count_documents(dict(session=sessionname,**kwargs))
    
    def get_all_paths(self, casename, collection="paths", sessionname="test1", **kwargs):
        for i in self.db[collection].find(dict(session=sessionname,**kwargs)):
            yield dict(**i,pathraw=json.loads(self.fs.get(i['path']).read().decode())) # project the large file



    def first(self, popname, casename, collection="paths", sessionname="test1", **kwargs):
        for i in self.get_paths(popname, casename, collection, sessionname, **kwargs):
            return i
    
    def get_times(self,collection="execs", **kwargs):
        for i in self.db[collection].find(dict(
                **kwargs
            )):
            # print(i)
            if i['times']:
                print(i)
                return json.loads(self.fs.get(i['times']).read().decode())

if __name__ == "__main__":
    repository = DBUtils()

    print(repository.count_paths("ams", "run_qr_str"))

    for p in repository.get_paths("ams", "run_qr_str"):
        print(len(p['pathraw']))

