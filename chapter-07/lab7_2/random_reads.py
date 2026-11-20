from pymongo import MongoClient
from pymongo.errors import PyMongoError
import argparse, random, time, statistics, json
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Random-read benchmark against working_set.")
    parser.add_argument("--reads", type=int, default=5000)
    args = parser.parse_args()
    client = MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=4000)
    try:
        client.admin.command("ping")
    except PyMongoError:
        print("MongoDB is not reachable. Start Docker Desktop and run `docker compose up -d`.")
        raise SystemExit(1)
    col = client["experiment7"]["working_set"]
    count = col.count_documents({})
    if count == 0:
        print("Collection is empty. Run `python lab7_2/generate_workload.py` first.")
        raise SystemExit(1)

    samples_ms = []
    found = 0
    for i in range(args.reads):
        key = random.randrange(count)
        t0 = time.perf_counter()
        doc = col.find_one({"_id": key})
        samples_ms.append((time.perf_counter() - t0) * 1000)
        found += doc is not None
    result = {
        "requested_reads": args.reads,
        "found": found,
        "mean_latency_ms": round(statistics.mean(samples_ms), 3),
        "median_latency_ms": round(statistics.median(samples_ms), 3),
        "min_latency_ms": round(min(samples_ms), 3),
        "max_latency_ms": round(max(samples_ms), 3),
        "throughput_reads_per_second": round(args.reads / (sum(samples_ms) / 1000), 2)
    }
    print("LAB 7.2 — RANDOM READ RESULTS (actual local run)")
    print(json.dumps(result, indent=2))
    Path("results").mkdir(exist_ok=True)
    Path("results/random_reads_results.json").write_text(json.dumps(result, indent=2))
    client.close()

if __name__ == "__main__":
    main()
