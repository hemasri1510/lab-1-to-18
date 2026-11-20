# Lab 5.1 Try It Yourself: $bucket - Small / Medium / Large
from pymongo import MongoClient
import json

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["sales_db"]
orders = db["orders"]

print("--- $bucket: Categorize Orders by Total Value ---")
pipeline_bucket = [
    {"$project": {
        "customer": 1, "product": 1,
        "totalValue": {"$multiply": ["$quantity", "$unit_price"]}
    }},
    {"$bucket": {
        "groupBy": "$totalValue",
        "boundaries": [0, 50, 200, 100000],
        "default": "Other",
        "output": {
            "count": {"$sum": 1},
            "orders": {"$push": {"customer": "$customer", "product": "$product", "total": "$totalValue"}},
            "totalRevenue": {"$sum": "$totalValue"}
        }
    }}
]
result = list(orders.aggregate(pipeline_bucket))
# Rename buckets for readability
labels = ["Small (under $50)", "Medium ($50-200)", "Large (over $200)"]
for i, doc in enumerate(result):
    print(f"\nCategory: {labels[i] if i < len(labels) else doc['_id']}")
    print(f"Count: {doc['count']}, Total Revenue: {doc['totalRevenue']}")
    for o in doc["orders"]:
        print(o)

with open("orders_bucket.json", "w") as f:
    json.dump(result, f, indent=2, default=str)
print("\nSaved orders_bucket.json")