# Lab 1.1 Try It Yourself: ScyllaDB, InfluxDB, ArangoDB
import json

data = [
    {"Product": "ScyllaDB", "Family": "Column-Family Store (Wide-Column) + Key-Value",
     "Reason": "Cassandra-compatible, stores data in wide rows, key-based access. Spans 2 families.",
     "Best For": "High-throughput, low latency, gaming, ad-tech",
     "Limitation": "Complex tuning, eventual consistency"},
    {"Product": "InfluxDB", "Family": "Time-Series (Column-Family variant)",
     "Reason": "Optimized for timestamped data, not pure 4 families. Closest to Column-Family.",
     "Best For": "IoT sensors, monitoring, metrics",
     "Limitation": "Not good for general documents or graphs"},
    {"Product": "ArangoDB", "Family": "Multi-Model - Document + Graph + Key-Value",
     "Reason": "Spans 3 families. Can store JSON documents, graphs and key-values in one DB.",
     "Best For": "Apps needing document + graph together",
     "Limitation": "Mastering all models is complex"},
]
print("Lab 1.1 Try It Yourself")
for d in data:
    print(f"\n{d['Product']} -> {d['Family']}")
    print(f"Reason: {d['Reason']}")
    print(f"Best For: {d['Best For']} | Limitation: {d['Limitation']}")

print("\nConclusion: ArangoDB and ScyllaDB do NOT fit neatly into one family - they are multi-model.")

with open("lab1_1_try.json", "w") as f:
    json.dump(data, f, indent=2)
print("Saved lab1_1_try.json")