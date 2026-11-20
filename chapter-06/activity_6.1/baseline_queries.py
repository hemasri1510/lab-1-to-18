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
print("MongoDB Atlas connected successfully!")

# ---------- Existing Database ----------
db = client["lab6_indexing"]
products = db["products"]

print("Total documents:", products.count_documents({}))


# ---------- Q1 ----------
print("\n========== QUERY 1 ==========")
print("Category = Electronics, Sort by Price")

q1 = products.find(
    {"category": "Electronics"}
).sort("price", 1)

e1 = q1.explain()["executionStats"]

print("Stage:", e1["executionStages"]["stage"])
print("Total Docs Examined:", e1["totalDocsExamined"])
print("Total Keys Examined:", e1["totalKeysExamined"])
print("Documents Returned:", e1["nReturned"])


# ---------- Q2 ----------
print("\n========== QUERY 2 ==========")
print("Price between 100 and 500")

q2 = products.find({
    "price": {"$gte": 100, "$lte": 500}
})

e2 = q2.explain()["executionStats"]

print("Stage:", e2["executionStages"]["stage"])
print("Total Docs Examined:", e2["totalDocsExamined"])
print("Total Keys Examined:", e2["totalKeysExamined"])
print("Documents Returned:", e2["nReturned"])


# ---------- Q3 ----------
print("\n========== QUERY 3 ==========")
print("Tag = gaming")

q3 = products.find({
    "tags": "gaming"
})

e3 = q3.explain()["executionStats"]

print("Stage:", e3["executionStages"]["stage"])
print("Total Docs Examined:", e3["totalDocsExamined"])
print("Total Keys Examined:", e3["totalKeysExamined"])
print("Documents Returned:", e3["nReturned"])


# ---------- Q5 ----------
print("\n========== QUERY 5 ==========")
print("Rating >= 4.5")

q5 = products.find({
    "rating": {"$gte": 4.5}
})

e5 = q5.explain()["executionStats"]

print("Stage:", e5["executionStages"]["stage"])
print("Total Docs Examined:", e5["totalDocsExamined"])
print("Total Keys Examined:", e5["totalKeysExamined"])
print("Documents Returned:", e5["nReturned"])