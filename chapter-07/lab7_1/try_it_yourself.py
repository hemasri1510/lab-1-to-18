
from pymongo import MongoClient
from bson import BSON
from time import perf_counter
import json
from pathlib import Path

client = MongoClient("mongodb://localhost:27017")
client.admin.command("ping")

db = client["experiment7"]
referenced = db["tyi71_referenced"]
embedded = db["tyi71_embedded"]

# Use separate collections so Lab 7.1's original data stays intact.
referenced.drop()
embedded.drop()

source = {
    "_id": "source-001",
    "name": "Training Threat Feed",
    "reliability": "high",
    "description": "Synthetic source for schema-design testing"
}

indicator_ref = {
    "_id": "indicator-ref-001",
    "type": "domain",
    "value": "malicious-example.test",
    "severity": "high",
    "source_id": source["_id"]
}

indicator_embedded = {
    "_id": "indicator-emb-001",
    "type": "domain",
    "value": "malicious-example.test",
    "severity": "high",
    "source": source
}

referenced.insert_one(indicator_ref)
db["tyi71_sources"].replace_one(
    {"_id": source["_id"]}, source, upsert=True
)
embedded.insert_one(indicator_embedded)

# Compare BSON sizes.
ref_size = len(BSON.encode(indicator_ref))
embedded_size = len(BSON.encode(indicator_embedded))

# Compare lookup time using the same number of repetitions.
iterations = 1000

start = perf_counter()
for _ in range(iterations):
    doc = referenced.find_one({"_id": "indicator-ref-001"})
    feed = db["tyi71_sources"].find_one(
        {"_id": doc["source_id"]}
    )
ref_time_ms = (perf_counter() - start) * 1000

start = perf_counter()
for _ in range(iterations):
    doc = embedded.find_one({"_id": "indicator-emb-001"})
    feed = doc["source"]
embedded_time_ms = (perf_counter() - start) * 1000

results = {
    "iterations": iterations,
    "referenced_document_bson_bytes": ref_size,
    "embedded_document_bson_bytes": embedded_size,
    "referenced_lookup_total_ms": round(ref_time_ms, 3),
    "embedded_lookup_total_ms": round(embedded_time_ms, 3),
    "note": "Timings are local measurements and can vary by run."
}

print("TRY IT YOURSELF 7.1 — EMBEDDING VS REFERENCING")
print(json.dumps(results, indent=2))
print("\nAnalysis:")
print("- Referencing separates the source into a reusable document.")
print("- Embedding returns indicator and source details in one document.")
print("- Embedding avoids a second lookup for this access pattern.")
print("- Referencing is more convenient when source data is shared or updated.")

Path("results").mkdir(exist_ok=True)
Path("results/try_it_yourself_7_1.json").write_text(
    json.dumps(results, indent=2)
)
print("\nSaved results/try_it_yourself_7_1.json")

client.close()
