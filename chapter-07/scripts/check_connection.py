from pymongo import MongoClient
from pymongo.errors import PyMongoError

URI = "mongodb://localhost:27017"
try:
    client = MongoClient(URI, serverSelectionTimeoutMS=4000)
    print("MongoDB server:", client.admin.command("ping"))
    print("Server version:", client.server_info().get("version", "unknown"))
    print("Database:", "experiment7")
    client.close()
except PyMongoError as exc:
    print("Could not connect to MongoDB.")
    print("Start Docker Desktop and run `docker compose up -d` from the project root.")
    print("Details:", exc)
    raise SystemExit(1)
