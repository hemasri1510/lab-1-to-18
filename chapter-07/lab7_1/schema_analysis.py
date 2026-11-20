from bson import BSON
from bson.errors import InvalidDocument
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import json
from pathlib import Path

URI = "mongodb://localhost:27017"
DB_NAME = "experiment7"

def size_bytes(document):
    return len(BSON.encode(document))

def main():
    client = MongoClient(URI, serverSelectionTimeoutMS=4000)
    try:
        client.admin.command("ping")
    except PyMongoError:
        print("MongoDB is not reachable. Start Docker Desktop and run `docker compose up -d`.")
        raise SystemExit(1)

    db = client[DB_NAME]
    # Small, synthetic threat-intelligence-style examples; no external site is scraped.
    indicators = [
        {
            "_id": f"indicator-{i:03d}",
            "type": "domain" if i % 2 == 0 else "ipv4",
            "value": f"sample-{i}.example" if i % 2 == 0 else f"192.0.2.{i}",
            "severity": ["low", "medium", "high"][i % 3],
            "source_ids": [f"source-{i % 4}", f"source-{(i + 1) % 4}"],
            "tags": ["training", "synthetic"],
            "first_seen": "2026-01-01T00:00:00Z",
            "metadata": {"confidence": 0.5 + (i % 5) / 10, "verified": bool(i % 2)}
        }
        for i in range(12)
    ]
    sources = [
        {"_id": f"source-{i}", "name": f"Training source {i}", "url": f"https://source{i}.example"}
        for i in range(4)
    ]

    db.indicators.delete_many({})
    db.sources.delete_many({})
    db.indicators.insert_many(indicators)
    db.sources.insert_many(sources)

    sizes = [{"_id": d["_id"], "type": d["type"], "bson_bytes": size_bytes(d)} for d in indicators]
    print("LAB 7.1 — SYNTHETIC PRODUCTION-STYLE SCHEMA")
    print(f"Inserted indicators: {db.indicators.count_documents({})}")
    print(f"Inserted sources: {db.sources.count_documents({})}")
    print("\nSample BSON sizes:")
    for row in sizes[:5]:
        print(f"  {row['_id']}: {row['bson_bytes']} bytes")
    print("\nDesign comparison:")
    print("- Embedding is suitable for small, bounded data that is read with its parent.")
    print("- Referencing is suitable for shared/reused data or independently changing records.")
    print("- The sample indicator references source documents by source_ids.")
    print(f"\nMongoDB's maximum BSON document size is 16 MiB (16,777,216 bytes).")
    # Demonstrate size calculation without inserting a large/invalid document.
    demo = {"_id": "size-demo", "payload": "x" * 1024}
    print(f"1 KiB payload example BSON size: {size_bytes(demo)} bytes")
    result = {
        "indicator_count": len(indicators),
        "source_count": len(sources),
        "sample_bson_sizes": sizes,
        "max_bson_document_bytes": 16 * 1024 * 1024,
        "oversize_insert_attempted": False
    }
    out = Path("results")
    out.mkdir(exist_ok=True)
    (out / "lab7_1_schema_results.json").write_text(json.dumps(result, indent=2))
    print("\nSaved actual run details to results/lab7_1_schema_results.json")
    client.close()

if __name__ == "__main__":
    main()
