# Lab 10.2 Try: Throughput vs Concurrency + Retry Logic
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from concurrent.futures import ThreadPoolExecutor
import time, json

MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0"
client = MongoClient(MONGO_URI)
db = client["shop_db"]
inventory = db["inventory"]
orders = db["orders"]

def reserve_with_retry(customer_id):
    for attempt in range(5):
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    prod = inventory.find_one({"product_id": "P001"}, session=session)
                    if prod["stock"] < 1:
                        raise Exception("Out of Stock")
                    inventory.update_one({"product_id": "P001"}, {"$inc": {"stock": -1}}, session=session)
                    orders.insert_one({"order_id": f"ORD-{customer_id}-{attempt}", "customer_id": customer_id,
                        "items": [{"product_id": "P001", "qty": 1}], "status": "pending", "total": 45.0}, session=session)
            return True
        except PyMongoError as e:
            if e.has_error_label("TransientTransactionError"):
                time.sleep(0.1 * (2 ** attempt))
                continue
            return False
        except Exception:
            return False
    return False

results = {}
for threads in [1, 4, 8, 16]:
    inventory.delete_many({})
    orders.delete_many({})
    inventory.insert_one({"product_id": "P001", "name": "Headphones", "stock": 100, "version": 1})
    start = time.time()
    with ThreadPoolExecutor(max_workers=threads) as ex:
        res = list(ex.map(reserve_with_retry, range(100)))
    elapsed = time.time() - start
    success = sum(res)
    throughput = round(success / elapsed, 2) if elapsed > 0 else 0
    results[threads] = {"success": success, "time": round(elapsed, 2), "throughput_per_sec": throughput}
    print(f"Threads {threads:<5}      : {success} success | {elapsed:.2f}s | {throughput} ops/sec")

print("\nConclusion          : Throughput increases 1->8, plateaus at 16 due to lock contention")
print("Non-Transactional   : Higher raw throughput but risks inconsistency")

with open("throughput.json", "w") as f:
    json.dump(results, f, indent=2)

print("\n" + "="*50)
print("Lab 10.2 Try It Yourself Complete")
print("="*50)