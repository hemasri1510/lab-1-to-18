from pymongo import MongoClient
from urllib.parse import quote_plus
import random
import time

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


# ---------- Create Test Documents ----------
def create_products(start, count):

    data = []

    for i in range(start, start + count):

        data.append({
            "name": f"Test Product {i}",
            "category": random.choice([
                "Electronics",
                "Books",
                "Clothing",
                "Home",
                "Sports"
            ]),
            "price": round(random.uniform(10, 5000), 2),
            "rating": round(random.uniform(1, 5), 1),
            "stock": random.randint(0, 500),
            "tags": random.sample([
                "new",
                "sale",
                "premium",
                "gaming",
                "office",
                "eco"
            ], random.randint(1, 3))
        })

    return data


# ---------- Remove Existing Test Collection ----------
test_products = db["activity_6_2_products"]
test_products.drop()

print("\nTest collection created.")


# ---------- INSERT WITHOUT INDEXES ----------
print("\n========== WITHOUT INDEXES ==========")

documents = create_products(0, 10000)

start_time = time.perf_counter()

test_products.insert_many(documents)

end_time = time.perf_counter()

time_without_indexes = end_time - start_time

print("Documents inserted: 10000")
print(
    "Insertion time:",
    round(time_without_indexes, 4),
    "seconds"
)


# ---------- CREATE 5 INDEXES ----------
print("\nCreating 5 indexes...")

test_products.create_index(
    [("category", 1)],
    name="category_idx"
)

test_products.create_index(
    [("price", 1)],
    name="price_idx"
)

test_products.create_index(
    [("rating", 1)],
    name="rating_idx"
)

test_products.create_index(
    [("stock", 1)],
    name="stock_idx"
)

test_products.create_index(
    [("tags", 1)],
    name="tags_idx"
)

print("5 indexes created.")


# ---------- INSERT WITH INDEXES ----------
print("\n========== WITH 5 INDEXES ==========")

documents = create_products(10000, 10000)

start_time = time.perf_counter()

test_products.insert_many(documents)

end_time = time.perf_counter()

time_with_indexes = end_time - start_time

print("Documents inserted: 10000")
print(
    "Insertion time:",
    round(time_with_indexes, 4),
    "seconds"
)


# ---------- CALCULATE SLOWDOWN ----------
slowdown = (
    (time_with_indexes - time_without_indexes)
    / time_without_indexes
) * 100

print("\n========== RESULT ==========")

print(
    "Without indexes:",
    round(time_without_indexes, 4),
    "seconds"
)

print(
    "With 5 indexes:",
    round(time_with_indexes, 4),
    "seconds"
)

print(
    "Percentage slowdown:",
    round(slowdown, 2),
    "%"
)

print("\nActivity 6.2 completed!")