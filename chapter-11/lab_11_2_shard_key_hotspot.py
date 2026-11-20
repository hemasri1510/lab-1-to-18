from pymongo import MongoClient
from datetime import datetime, timedelta
import random

client = MongoClient("mongodb://admin:password123@localhost:27017/?authSource=admin")
db = client["shard_lab"]

# hotspot_data: monotonically increasing timestamp
base = datetime(2025, 1, 1)
db.hotspot_data.insert_many([
    {"ts": base + timedelta(seconds=i), "val": i} 
    for i in range(10000)
])

# even_data: random hashed key
db.even_data.insert_many([
    {"user_id": f"user_{random.randint(1,100000)}", "val": i} 
    for i in range(10000)
])