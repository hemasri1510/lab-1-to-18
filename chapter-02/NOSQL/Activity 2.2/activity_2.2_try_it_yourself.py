from pymongo import MongoClient

# Connect to local MongoDB
client = MongoClient("mongodb://localhost:27017")

db = client["bookstore_db"]
collection = db["books"]

# Clear previous data
collection.delete_many({})

# Insert sample books
books = [
    {"title": "Python Crash Course", "year": 2022, "price": 45.00},
    {"title": "Learning Python", "year": 2019, "price": 50.00},
    {"title": "Data Science Handbook", "year": 2021, "price": 60.00},
    {"title": "Machine Learning Basics", "year": 2023, "price": 55.00},
    {"title": "Clean Code", "year": 2008, "price": 40.00}
]

collection.insert_many(books)

print("=== BOOKSTORE CRUD - TRY IT YOURSELF ===")

# READ: Books published before 2010
print("\nBooks published before 2010:")
for book in collection.find({"year": {"$lt": 2010}}):
    print(book["title"], "-", book["year"])

# READ: Books with price below 50
print("\nBooks priced below $50:")
for book in collection.find({"price": {"$lt": 50}}):
    print(book["title"], "-", book["price"])

# UPDATE: Increase prices of books published before 2010 by 10%
collection.update_many(
    {"year": {"$lt": 2010}},
    {"$mul": {"price": 1.10}}
)

print("\nPrices after 10% increase:")
for book in collection.find({}):
    print(book["title"], "-", round(book["price"], 2))

# DELETE: Remove one book
collection.delete_one({"title": "Clean Code"})

print("\nAfter deleting Clean Code:")
for book in collection.find({}):
    print(book["title"])

print("\n=== Try It Yourself Complete ===")