from pymongo.mongo_client import MongoClient;
from pymongo.server_api import ServerApi;

uri = "mongodb+srv://zphrstn:Eclipse_1452@test.1gfxxye.mongodb.net/?appName=test"
mongodb_client = MongoClient(uri, server_api=ServerApi('1'))

try:
    mongodb_client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

mydb = mongodb_client["test_database"]


