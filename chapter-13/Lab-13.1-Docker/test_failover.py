
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import time

uri = "mongodb://admin:password123@mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0&authSource=admin"

client = MongoClient(uri, serverSelectionTimeoutMS=5000)

db = client["lab13"]
collection = db["failover_test"]

# Insert a test document
collection.insert_one({
    "message": "MongoDB replica set failover test",
    "status": "active"
})

print("Connected to MongoDB replica set!")
print("Starting continuous read test...\n")

while True:
    try:
        document = collection.find_one({"status": "active"})
        print("Read successful:", document["message"])

    except PyMongoError as error:
        print("Connection interrupted. Waiting for new primary...")
        print(error)

    time.sleep(2)
