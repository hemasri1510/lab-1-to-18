import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Connect to Docker MongoDB
local_client = MongoClient("mongodb://localhost:27017")
local_info = local_client.server_info()

# Connect to MongoDB Atlas
atlas_client = MongoClient(
    os.getenv("MONGO_URI_ATLAS"),
    serverSelectionTimeoutMS=10000
)
atlas_info = atlas_client.server_info()

print("MongoDB Connection Details")
print("==========================")

print("\nDocker MongoDB")
print("Status  : Connected")
print("Version :", local_info["version"])

print("\nMongoDB Atlas")
print("Status  : Connected")
print("Version :", atlas_info["version"])

print("\nVersion Comparison")
print("==================")

if local_info["version"] == atlas_info["version"]:
    print("Both MongoDB servers use the same version.")
else:
    print("The MongoDB servers use different versions.")