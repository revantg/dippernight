from mongo_creds import *
from sshtunnel import SSHTunnelForwarder
import pymongo
import json
import pickle

server = SSHTunnelForwarder(
    MONGO_HOST,
    ssh_username=MONGO_USER,
    ssh_password=MONGO_PASS,
    remote_bind_address=('127.0.0.1', 27017)
)

server.start()

client = pymongo.MongoClient('127.0.0.1', server.local_bind_port)
db = client[MONGO_DB]
print(db.collection_names())

with open("scraped_data.pickle", "rb") as f:
    json_data = pickle.load(f)

coll = db['ecl_allotment_analysis']
coll.insert(json_data)

server.stop()
