from pymongo import MongoClient
from pymongo.errors import PyMongoError
import argparse, time, json
from datetime import datetime, timezone
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Sample MongoDB serverStatus/WiredTiger cache metrics.")
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--interval", type=int, default=10)
    args = parser.parse_args()
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=4000)
    try:
        client.admin.command("ping")
    except PyMongoError:
        print("MongoDB is not reachable. Start Docker Desktop and run `docker compose up -d`.")
        raise SystemExit(1)

    rows = []
    for i in range(args.samples):
        status = client.admin.command("serverStatus")
        wt = status.get("wiredTiger", {}).get("cache", {})
        row = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "sample": i + 1,
            "resident_megabytes": round(status.get("resident", 0), 2),
            "wiredTiger_cache_bytes_currently_in_cache": wt.get("bytes currently in the cache"),
            "wiredTiger_cache_max_bytes_configured": wt.get("maximum bytes configured"),
            "pages_read_into_cache": wt.get("pages read into cache"),
            "pages_written_from_cache": wt.get("pages written from cache"),
            "tracked_dirty_bytes": wt.get("tracked dirty bytes in the cache")
        }
        rows.append(row)
        print(json.dumps(row, indent=2))
        if i < args.samples - 1:
            time.sleep(args.interval)

    Path("results").mkdir(exist_ok=True)
    Path("results/cache_monitor_results.json").write_text(json.dumps(rows, indent=2))
    print("Saved actual samples to results/cache_monitor_results.json")
    client.close()

if __name__ == "__main__":
    main()
