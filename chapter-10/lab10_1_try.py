# Lab 10.1 Try: Retry with Exponential Backoff
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import time, json

MONGO_URI = "mongodb://localhost:27017/?replicaSet=rs0"
client = MongoClient(MONGO_URI)
db = client["bank_db"]
accounts = db["accounts"]

def transfer_with_retry(from_id, to_id, amount, max_retries=5):
    for attempt in range(max_retries):
        try:
            with client.start_session() as session:
                with session.start_transaction():
                    src = accounts.find_one({"account_id": from_id}, session=session)
                    if src["balance"] < amount:
                        raise Exception("Insufficient Funds")
                    accounts.update_one({"account_id": from_id, "balance": {"$gte": amount}},
                        {"$inc": {"balance": -amount}}, session=session)
                    accounts.update_one({"account_id": to_id},
                        {"$inc": {"balance": amount}}, session=session)
            print(f"Attempt {attempt+1:<5}       : SUCCESS")
            return True
        except PyMongoError as e:
            # Check TransientTransactionError label
            if e.has_error_label("TransientTransactionError") and attempt < max_retries-1:
                wait = 0.1 * (2 ** attempt)  # 0.1, 0.2, 0.4, 0.8
                print(f"Attempt {attempt+1:<5}       : TransientTransactionError - Retrying in {wait}s")
                time.sleep(wait)
                continue
            print(f"Attempt {attempt+1:<5}       : FAILED - {e}")
            return False

print("Lab 10.1 Try It Yourself - Exponential Backoff")
print("Transfer A101 -> A102 : 100 Rs")
transfer_with_retry("A101", "A102", 100)

for acc in accounts.find({}, {"_id": 0}).sort("account_id"):
    print(f"{acc['account_id']:<15}: {acc['balance']} Rs")

with open("accounts_retry.json", "w") as f:
    json.dump(list(accounts.find({}, {"_id": 0})), f, indent=2)

print("\n" + "="*50)
print("Lab 10.1 Try It Yourself Complete")
print("="*50)