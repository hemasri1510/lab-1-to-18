import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Connect to local MongoDB (Docker)
local_client = MongoClient("mongodb://localhost:27017")
local_version = local_client.server_info()["version"]

# Connect to MongoDB Atlas
atlas_uri = os.getenv("MONGO_URI_ATLAS")
atlas_client = MongoClient(atlas_uri, serverSelectionTimeoutMS=10000)
atlas_version = atlas_client.server_info()["version"]

# Display and compare versions
print("MongoDB Server Version Comparison")
print("----------------------------------")
print("Docker MongoDB Version :", local_version)
print("MongoDB Atlas Version  :", atlas_version)

if local_version == atlas_version:
    print("Result: Both servers are running the same version.")
else:
    print("Result: The servers are running different versions.")