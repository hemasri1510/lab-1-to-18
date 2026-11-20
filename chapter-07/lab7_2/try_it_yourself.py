
import time
import json
from datetime import datetime, timezone
from pathlib import Path

import requests
from pymongo import MongoClient

MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "experiment7"
COLLECTION = "threat_reports"

# Public CISA Known Exploited Vulnerabilities catalog
FEED_URL = (
    "https://www.cisa.gov/sites/default/files/feeds/"
    "known_exploited_vulnerabilities.json"
)

INTERVAL_SECONDS = 10
SAMPLES = 6


def get_cache_stats(client):
    status = client.admin.command("serverStatus")
    cache = status.get("wiredTiger", {}).get("cache", {})

    return {
        "pages_requested": cache.get("pages requested from the cache"),
        "pages_read": cache.get("pages read into cache"),
    }


def calculate_hit_ratio(previous, current):
    requested_before = previous.get("pages_requested")
    requested_now = current.get("pages_requested")
    read_before = previous.get("pages_read")
    read_now = current.get("pages_read")

    if None in (
        requested_before, requested_now, read_before, read_now
    ):
        return None

    requested = requested_now - requested_before
    pages_read = read_now - read_before

    if requested <= 0:
        return None

    hits = max(0, requested - pages_read)
    return round((hits / requested) * 100, 2)


def check_new_reports(collection):
    response = requests.get(FEED_URL, timeout=20)
    response.raise_for_status()
    reports = response.json().get("vulnerabilities", [])

    new_count = 0

    for report in reports:
        cve_id = report.get("cveID")
        if not cve_id:
            continue

        result = collection.update_one(
            {"_id": cve_id},
            {
                "$setOnInsert": {
                    "cveID": cve_id,
                    "vendorProject": report.get("vendorProject"),
                    "product": report.get("product"),
                    "vulnerabilityName": report.get("vulnerabilityName"),
                    "dateAdded": report.get("dateAdded"),
                    "source": "CISA KEV",
                    "first_seen_utc": datetime.now(
                        timezone.utc
                    ).isoformat(),
                }
            },
            upsert=True,
        )

        if result.upserted_id is not None:
            new_count += 1
            print(
                f"NEW REPORT: {cve_id} — "
                f"{report.get('vulnerabilityName', 'Unknown')}"
            )

    return len(reports), new_count


def main():
    client = MongoClient(
        MONGO_URI, serverSelectionTimeoutMS=5000
    )
    client.admin.command("ping")
    collection = client[DB_NAME][COLLECTION]

    print("TRY IT YOURSELF 7.2 — THREAT AND CACHE MONITOR")
    print(f"Checking every {INTERVAL_SECONDS} seconds.")
    print("First run may import existing CISA catalog entries.")
    print("Press Ctrl+C to stop.\n")

    previous = get_cache_stats(client)
    history = []

    try:
        for sample in range(1, SAMPLES + 1):
            total_reports, new_reports = check_new_reports(
                collection
            )
            current = get_cache_stats(client)
            hit_ratio = calculate_hit_ratio(previous, current)

            row = {
                "timestamp_utc": datetime.now(
                    timezone.utc
                ).isoformat(),
                "sample": sample,
                "catalog_entries_seen": total_reports,
                "new_reports_added": new_reports,
                "database_report_count": collection.count_documents({}),
                "cache_hit_ratio_percent": hit_ratio,
            }
            history.append(row)

            print(json.dumps(row, indent=2))
            previous = current

            if sample < SAMPLES:
                time.sleep(INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nMonitoring stopped by user.")
    except requests.RequestException as exc:
        print(f"Could not fetch the public catalog: {exc}")
    finally:
        Path("results").mkdir(exist_ok=True)
        Path("results/try_it_yourself_7_2.json").write_text(
            json.dumps(history, indent=2)
        )
        print(
            "\nSaved results to "
            "results/try_it_yourself_7_2.json"
        )
        client.close()


if __name__ == "__main__":
    main()
