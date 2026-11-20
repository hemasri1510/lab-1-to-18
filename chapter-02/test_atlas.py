import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

uri = os.getenv("MONGO_URI_ATLAS")

client = MongoClient(uri, serverSelectionTimeoutMS=10000)

print("Atlas version:", client.server_info()["version"])
print("Atlas connection: SUCCESS")