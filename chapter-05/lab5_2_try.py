# Lab 5.2 Try It Yourself: $lookup with pipeline sub-expression
from pymongo import MongoClient
from bson import ObjectId
import json

MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["sales_db"]
products = db["products"]
orders2 = db["orders_lookup"]

print("--- $lookup with Pipeline: Only Electronics products, quantity >= 2 ---")
pipeline = [
    {"$lookup": {
        "from": "orders_lookup",
        "let": {"pid": "$_id"},
        "pipeline": [
            {"$match": {"$expr": {"$eq": ["$product_id", "$$pid"]}}},
            {"$match": {"quantity": {"$gte": 2}}},  # Filter on foreign side BEFORE join
            {"$project": {"_id": 0, "customer": 1, "quantity": 1, "order_date": 1}}
        ],
        "as": "filtered_orders"
    }},
    {"$match": {"category": "Electronics"}},  # Filter on local side
    {"$project": {"_id": 0, "name": 1, "category": 1, "base_price": 1, "filtered_orders": 1}}
]
result = list(products.aggregate(pipeline))
for doc in result:
    print(doc)

with open("products_orders_pipeline.json", "w") as f:
    json.dump(result, f, indent=2, default=str)
print("\nSaved products_orders_pipeline.json")
