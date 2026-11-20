from pymongo import MongoClient
from urllib.parse import quote_plus

# ---------- Atlas Connection ----------
username = "hemasri151006_db_user"
password = "hemasri1510"

encoded_password = quote_plus(password)

cluster_address = "cluster0.7s7y5po.mongodb.net"

uri = f"mongodb+srv://{username}:{encoded_password}@{cluster_address}/"

client = MongoClient(
    uri,
    tls=True,
    serverSelectionTimeoutMS=30000
)

client.admin.command("ping")

db = client["lab6_indexing"]
products = db["products"]

print("MongoDB Atlas connected successfully!")
print("Total documents:", products.count_documents({}))


# ---------- Create Compound Index ----------
print("\nCreating compound index...")




print("Compound index created.")


# ---------- Covered Query ----------
print("\n========== COVERED QUERY ==========")

query = {
    "category": "Electronics",
    "price": {
        "$gte": 100,
        "$lte": 500
    }
}

projection = {
    "_id": 0,
    "category": 1,
    "price": 1
}

result = products.find(
    query,
    projection
).hint([("category", 1), ("price", 1)])

explain = result.explain()

stats = explain["executionStats"]

print("Stage:", stats["executionStages"]["stage"])
print("Total Docs Examined:", stats["totalDocsExamined"])
print("Total Keys Examined:", stats["totalKeysExamined"])
print("Documents Returned:", stats["nReturned"])

print("\nExpected for a covered query:")
print("Total Docs Examined = 0")
print("No FETCH stage required")

print("\nActivity 6.2 Try Yourself completed!")