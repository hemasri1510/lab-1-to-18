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

db = client["lab6_indexing"]
products = db["products"]

print("Total documents:", products.count_documents({}))


# ---------- CREATE INDEXES ----------
print("\n========== CREATING INDEXES ==========")

products.create_index(
    [("category", 1), ("price", 1)],
    name="category_price_idx"
)

products.create_index(
    [("price", 1)],
    name="price_idx"
)

products.create_index(
    [("tags", 1)],
    name="tags_idx"
)

products.create_index(
    [("name", "text")],
    name="name_text_idx"
)

products.create_index(
    [("rating", 1)],
    name="rating_idx"
)

print("All indexes created successfully!")

print("\nIndexes:")
for index in products.list_indexes():
    print(index["name"])


# ---------- Q1 ----------
print("\n========== QUERY 1 ==========")

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

q3 = products.find({
    "tags": "gaming"
})

e3 = q3.explain()["executionStats"]

print("Stage:", e3["executionStages"]["stage"])
print("Total Docs Examined:", e3["totalDocsExamined"])
print("Total Keys Examined:", e3["totalKeysExamined"])
print("Documents Returned:", e3["nReturned"])


# ---------- Q4 ----------
print("\n========== QUERY 4 ==========")

q4 = products.find({
    "$text": {"$search": "Phone"}
})

e4 = q4.explain()["executionStats"]

print("Stage:", e4["executionStages"]["stage"])
print("Total Docs Examined:", e4["totalDocsExamined"])
print("Total Keys Examined:", e4["totalKeysExamined"])
print("Documents Returned:", e4["nReturned"])


# ---------- Q5 ----------
print("\n========== QUERY 5 ==========")

q5 = products.find({
    "rating": {"$gte": 4.5}
})

e5 = q5.explain()["executionStats"]

print("Stage:", e5["executionStages"]["stage"])
print("Total Docs Examined:", e5["totalDocsExamined"])
print("Total Keys Examined:", e5["totalKeysExamined"])
print("Documents Returned:", e5["nReturned"])