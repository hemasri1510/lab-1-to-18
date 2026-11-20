from pymongo import MongoClient, ASCENDING
from pymongo.errors import PyMongoError
import random, string, time

URI = "mongodb://localhost:27017"
DB_NAME = "experiment7"
COLLECTION = "working_set"
TARGET_DOCS = 100_000
TARGET_PAYLOAD_BYTES = 1800  # about 2 KB overall after BSON fields

def random_text(length):
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))

def main():
    client = MongoClient(URI, serverSelectionTimeoutMS=4000)
    try:
        client.admin.command("ping")
    except PyMongoError:
        print("MongoDB is not reachable. Start Docker Desktop and run `docker compose up -d`.")
        raise SystemExit(1)
    col = client[DB_NAME][COLLECTION]
    confirm = input(f"This recreates only {DB_NAME}.{COLLECTION}. Type YES to continue: ")
    if confirm != "YES":
        print("Cancelled; no collection changed.")
        client.close()
        return

    col.drop()
    batch = []
    started = time.perf_counter()
    for i in range(TARGET_DOCS):
        batch.append({
            "_id": i,
            "category": ["high", "medium", "low"][i % 3],
            "score": round(random.random(), 4),
            "label": f"sample-{i % 1000}",
            "payload": random_text(TARGET_PAYLOAD_BYTES)
        })
        if len(batch) == 1000:
            col.insert_many(batch, ordered=False)
            batch.clear()
            if (i + 1) % 10000 == 0:
                print(f"Inserted {i + 1:,}/{TARGET_DOCS:,}")
    if batch:
        col.insert_many(batch, ordered=False)
    col.create_index([("category", ASCENDING)])
    elapsed = time.perf_counter() - started
    count = col.count_documents({})
    stats = col.database.command("collStats", COLLECTION)
    print(f"\nActual inserted count: {count:,}")
    print(f"Elapsed time: {elapsed:.2f} seconds")
    print(f"Storage size: {stats.get('storageSize', 0):,} bytes")
    print(f"Average object size: {stats.get('avgObjSize', 0):,.0f} bytes")
    print("Index created: category_1")
    client.close()

if __name__ == "__main__":
    main()
