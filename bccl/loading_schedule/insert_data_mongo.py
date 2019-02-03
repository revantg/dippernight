from mongo_creds import *
from sshtunnel import SSHTunnelForwarder
import pymongo
import json

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

with open("final_data.json") as f:
    json_data = json.load(f)

coll = db['loading_schedules']
coll.insert(json_data)

server.stop()

# for element in a[1:]:
#     temp = {}
#     for attribute in element:
#         if attribute in "colliery_data": continue
#         temp[attribute] = element[attribute]
#     for data in element['colliery_data']:
#         record = temp.copy()
#         for attribute in data:
#             record[attribute] = data[attribute]
#         final_json.append(record)

