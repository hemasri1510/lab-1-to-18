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


# ---------- Run Queries Multiple Times ----------
print("\nRunning queries...")

for i in range(10):

    list(
        products.find({"category": "Electronics"})
        .sort("price", 1)
        .limit(100)
    )

    list(
        products.find({
            "price": {"$gte": 100, "$lte": 500}
        }).limit(100)
    )

    list(
        products.find({"tags": "gaming"})
        .limit(100)
    )

    list(
        products.find({
            "$text": {"$search": "Phone"}
        }).limit(100)
    )

    list(
        products.find({
            "rating": {"$gte": 4.5}
        }).limit(100)
    )

print("Queries completed!")


# ---------- Check Index Usage ----------
print("\n========== INDEX USAGE ==========")

stats = list(
    products.aggregate([
        {"$indexStats": {}}
    ])
)

for stat in stats:
    print(
        "Index:",
        stat["name"],
        "| Operations:",
        stat["accesses"]["ops"]
    )

print("\nIndex statistics completed!")