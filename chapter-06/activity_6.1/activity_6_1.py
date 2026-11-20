from pymongo import MongoClient
from urllib.parse import quote_plus
import random

# Type your Atlas username here
username = "hemasri151006_db_user"

# Type your actual Atlas password here
password = "hema1510"

# Encode special characters like @, #, %, etc.
encoded_password = quote_plus(password)

# Paste ONLY the cluster address from your Atlas connection string
cluster_address = "cluster0.7s7y5po.mongodb.net"

uri = f"mongodb+srv://{username}:{encoded_password}@{cluster_address}/"

client = MongoClient(uri)

# Test connection
client.admin.command("ping")

print("MongoDB Atlas connected successfully!")
# ---------- Database and Collection ----------
db = client["lab6_indexing"]
products = db["products"]

# Start fresh
products.drop()

# ---------- Product Data ----------
categories = [
    "Electronics",
    "Books",
    "Clothing",
    "Home",
    "Sports",
    "Beauty",
    "Toys",
    "Grocery"
]

tag_pool = [
    "new",
    "sale",
    "premium",
    "popular",
    "eco",
    "wireless",
    "gaming",
    "office",
    "student",
    "travel"
]

product_types = [
    "Phone",
    "Laptop",
    "Shirt",
    "Book",
    "Bottle",
    "Headset"
]

products_data = []

# Generate 50,000 products
for i in range(50000):
    product = {
        "name": f"Product {i:05d} {random.choice(product_types)}",
        "category": random.choice(categories),
        "price": round(random.uniform(10, 5000), 2),
        "rating": round(random.uniform(1, 5), 1),
        "stock": random.randint(0, 500),
        "tags": random.sample(tag_pool, random.randint(1, 4))
    }

    products_data.append(product)

# Insert in smaller batches
for start in range(0, 50000, 250):
    batch = products_data[start:start + 250]
    products.insert_many(batch)

    if (start + len(batch)) % 2500 == 0:
        print(f"Inserted {start + len(batch)} / 50000")

print("50,000 products inserted successfully!")
print("Total documents:", products.count_documents({}))
# ---------- Five Representative Queries ----------

print("\n--- Query 1: Find by category and sort by price ---")
query1 = products.find(
    {"category": "Electronics"}
).sort("price", 1)

print(query1.explain())


print("\n--- Query 2: Find by price range ---")
query2 = products.find({
    "price": {"$gte": 100, "$lte": 500}
})

print(query2.explain())


print("\n--- Query 3: Find by tag ---")
query3 = products.find({
    "tags": "gaming"
})

print(query3.explain())


print("\n--- Query 4: Text search on name ---")
# Text index is required for $text search.
# We will create this index later, so skip this query for now.

print("Query 4 will be run after creating the text index.")


print("\n--- Query 5: Find by rating ---")
query5 = products.find({
    "rating": {"$gte": 4.5}
})

print(query5.explain())
# ---------- Query 4: Text Search ----------
print("\n--- Query 4: Text search on name ---")

products.create_index(
    [("name", "text")],
    name="name_text_idx"
)

query4 = products.find({
    "$text": {"$search": "Phone"}
})

print(query4.explain())