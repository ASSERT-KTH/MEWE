from peewee import *
from common.common import *
from datetime import date
import json

db = SqliteDatabase(f'{OUT_FOLDER}/fastly4edge.db')



class TCPSample(Model):

    time=DoubleField()
    test_name=CharField()
    pop_name=CharField()
    pop_ip=CharField()
    uri=CharField()
    at=IntegerField()
    
    tcp_rtts_json=TextField() # saved as raw json
    frames_rtts_json=TextField() # saved as raw json
    user_space_json=TextField() # saved as raw json
    header_times=TextField() # saved as raw json

    class Meta:
        database=db

    # TODO get and set json fields

class DeployEvent(Model):

    pop_name=CharField()
    pop_at=IntegerField()
    time=DoubleField()
    response=TextField()
    tpe=CharField()


    class Meta:
        database = db

def create_db():
    db.connect()
    db.create_tables([TCPSample, DeployEvent])

