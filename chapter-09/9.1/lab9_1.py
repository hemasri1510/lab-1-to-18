"""
Lab 9.1 — Measure MongoDB write concern latency.

Run this script from a Python environment that can resolve the replica-set member
hostnames in the replica-set configuration. For this lab, running it in a Python
container on the same Docker network as the MongoDB containers is recommended.

Environment variables:
  MONGO_URI      Replica-set URI (default is for lab81-mongo1/2/3)
  DOCS_PER_TEST  Number of documents per test (default 1000)
  WTIMEOUT_MS    Write-concern timeout (default 10000)

Important: MongoDB does not define w="all" as a built-in write concern.
For a three-data-bearing-member replica set, w=3 waits for all three members.
"""

import csv
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient, WriteConcern
from pymongo.errors import PyMongoError


URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017,localhost:27018,localhost:27019/?replicaSet=rs0"
)

N = int(os.getenv("DOCS_PER_TEST", "1000"))
WTIMEOUT_MS = int(os.getenv("WTIMEOUT_MS", "10000"))
OUT_CSV = Path("lab9_1_results.csv")
OUT_TXT = Path("lab9_1_output.txt")

# "all" is represented by w=3 for this three-data-bearing-member replica set.
TESTS = [
    ("w:1, j:true", 1, True),
    ("w:majority, j:true", "majority", True),
    ("w:3 (all data members), j:true", 3, True),
    ("w:1, j:false", 1, False),
    ("w:majority, j:false", "majority", False),
    ("w:3 (all data members), j:false", 3, False),
]

def main():
    rows = []
    run_id = str(uuid.uuid4())
    lines = [
        "Lab 9.1 — Write Concern Latency",
        f"Run ID: {run_id}",
        f"Started UTC: {datetime.now(timezone.utc).isoformat()}",
        f"Documents per test: {N}",
        "Note: MongoDB's built-in write concern does not support w='all'; w=3 is used for three data-bearing members.",
        ""
    ]

    client = MongoClient(URI, serverSelectionTimeoutMS=5000, connectTimeoutMS=5000)
    try:
        client.admin.command("ping")
        print("Connected to replica set.")
        print(f"Replica-set URI: {URI}")
        print(f"Testing {N} documents per write concern...")
        for label, w, journal in TESTS:
            collection_name = f"lab9_1_{run_id.replace('-', '')[:10]}"
            collection = client["lab9"][collection_name].with_options(
                write_concern=WriteConcern(w=w, j=journal, wtimeout=WTIMEOUT_MS)
            )
            started = time.perf_counter()
            success = 0
            error_text = ""
            try:
                for i in range(N):
                    collection.insert_one({
                        "runId": run_id,
                        "test": label,
                        "sequence": i + 1,
                        "createdAt": datetime.now(timezone.utc),
                        "payload": "x" * 32
                    })
                    success += 1
            except PyMongoError as exc:
                error_text = f"{type(exc).__name__}: {exc}"
            elapsed = time.perf_counter() - started
            average_ms = (elapsed / success * 1000) if success else None
            row = {
                "test": label,
                "w": str(w),
                "j": str(journal).lower(),
                "requested_documents": N,
                "successful_documents": success,
                "elapsed_seconds": round(elapsed, 6),
                "average_latency_ms": round(average_ms, 4) if average_ms is not None else "",
                "status": "COMPLETE" if success == N else "INCOMPLETE/ERROR",
                "error": error_text
            }
            rows.append(row)
            summary = (
                f"{label}: {success}/{N} successful; total={elapsed:.4f}s; "
                f"average={average_ms:.4f}ms/write" if average_ms is not None
                else f"{label}: 0/{N} successful; total={elapsed:.4f}s; ERROR={error_text}"
            )
            print(summary)
            lines.append(summary)
            if error_text:
                lines.append(f"  Error: {error_text}")

        with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        lines.extend([
            "",
            "Interpretation:",
            "- w=1 waits for the primary's acknowledgment.",
            "- w=majority waits for the replica-set voting majority's acknowledgment.",
            "- w=3 waits for acknowledgments from all three data-bearing members in this lab.",
            "- j=true requests journal acknowledgment; j=false does not explicitly require it.",
            "- Actual timing depends on storage, Docker/host load, journaling, and replica-set state.",
            "- Do not assume a fixed 2–5x difference; use the measured values in the CSV."
        ])
        OUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\nSaved: {OUT_CSV.resolve()}")
        print(f"Saved: {OUT_TXT.resolve()}")
    finally:
        client.close()

if __name__ == "__main__":
    main()
