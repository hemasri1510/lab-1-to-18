"""
Lab 9.2 — Observe a network partition and write-concern behavior.

Run inside the Docker network shared by the replica-set containers. This script
prints replica-set member states and attempts one w:1 and one w:majority insert
each cycle. It records successes/errors to CSV and text.

Do NOT run this against production. Disconnect only a lab secondary. Restore the
network after the exercise. A write with w:1 can succeed on a primary even when
a secondary is isolated; majority writes need acknowledgments from a majority.
"""

import csv
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from pymongo import MongoClient, WriteConcern
from pymongo.errors import PyMongoError

URI = os.getenv(
    "MONGO_URI",
    "mongodb://lab81-mongo1:27017,lab81-mongo2:27017,lab81-mongo3:27017/"
    "?replicaSet=rs0&serverSelectionTimeoutMS=4000"
)
INTERVAL = float(os.getenv("POLL_SECONDS", "3"))
CSV_PATH = Path("lab9_2_partition_observations.csv")
TXT_PATH = Path("lab9_2_output.txt")

def append_csv(row):
    exists = CSV_PATH.exists()
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(row)

def status_snapshot(client):
    try:
        result = client.admin.command("replSetGetStatus")
        members = result.get("members", [])
        return "; ".join(
            f"{m.get('name')}={m.get('stateStr')} (health={m.get('health')})"
            for m in members
        )
    except PyMongoError as exc:
        return f"status error: {type(exc).__name__}: {exc}"

def test_write(uri, concern, label):
    client = None
    started = time.perf_counter()
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=4000, connectTimeoutMS=3000)
        client.admin.command("ping")
        collection = client["lab9"]["partition_test"].with_options(
            write_concern=WriteConcern(w=concern, j=True, wtimeout=5000)
        )
        result = collection.insert_one({
            "test": label,
            "writeConcern": str(concern),
            "createdAt": datetime.now(timezone.utc)
        })
        return "SUCCESS", str(result.inserted_id), round(time.perf_counter() - started, 4)
    except PyMongoError as exc:
        return "FAILED/TIMED OUT", f"{type(exc).__name__}: {exc}", round(time.perf_counter() - started, 4)
    finally:
        if client is not None:
            client.close()

def main():
    print("Lab 9.2 observer started. Press Ctrl+C to stop.")
    print("Disconnect/reconnect a SECONDARY from a separate PowerShell window.")
    client = MongoClient(URI, serverSelectionTimeoutMS=4000, connectTimeoutMS=3000)
    try:
        while True:
            timestamp = datetime.now(timezone.utc).isoformat()
            try:
                client.admin.command("ping")
                state = status_snapshot(client)
            except PyMongoError as exc:
                state = f"topology/connection error: {type(exc).__name__}: {exc}"
            print(f"\n[{timestamp}] {state}", flush=True)
            with TXT_PATH.open("a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {state}\n")

            for label, concern in [("w1", 1), ("majority", "majority")]:
                result, detail, elapsed = test_write(URI, concern, label)
                event_time = datetime.now(timezone.utc).isoformat()
                print(f"  {label}: {result}; elapsed={elapsed}s; {detail}", flush=True)
                row = {
                    "timestamp_utc": event_time,
                    "test": label,
                    "write_concern": str(concern),
                    "result": result,
                    "elapsed_seconds": elapsed,
                    "detail": detail,
                    "replica_set_status": state
                }
                append_csv(row)
                with TXT_PATH.open("a", encoding="utf-8") as f:
                    f.write(f"  {label}: {result}; elapsed={elapsed}s; {detail}\n")
            time.sleep(INTERVAL)
    except KeyboardInterrupt:
        print("\nObserver stopped. Output saved to lab9_2_output.txt and lab9_2_partition_observations.csv.")
    finally:
        client.close()

if __name__ == "__main__":
    main()
