import os

from pymongo import MongoClient
from dotenv import load_dotenv


load_dotenv()


def get_db(db_name="nosql_labs"):
    uri = os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017"
    )

    client = MongoClient(uri)

    print(f"[OK] Connected to MongoDB at {uri}")

    return client[db_name]


def reset_collection(db, collection_name):
    if collection_name in db.list_collection_names():
        db.drop_collection(collection_name)


def print_json(data):
    import json

    print(
        json.dumps(
            data,
            indent=2,
            default=str
        )
    )


def banner(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)