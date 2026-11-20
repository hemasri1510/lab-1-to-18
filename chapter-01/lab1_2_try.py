# Lab 1.2 Try It Yourself: Healthcare Application Mapping
import json

data = [
    {"Data Domain": "Patient Profiles", "Family": "Document (MongoDB)", "Why": "Each patient has different reports, nested history, prescriptions - flexible schema"},
    {"Data Domain": "Vital Signs / IoT Sensors", "Family": "Column-Family / Time-Series (Cassandra/InfluxDB)", "Why": "Heart rate, BP every second - high write, time-range query"},
    {"Data Domain": "Doctor-Patient Referral Graph", "Family": "Graph (Neo4j)", "Why": "Find specialist, referral chain, disease spread - traversal"},
    {"Data Domain": "Medicine Stock / Cache", "Family": "Key-Value (Redis)", "Why": "Fast lookup by medicine ID, availability, session cache"},
]
print("Lab 1.2 Try It Yourself - Healthcare App")
for d in data:
    print(f"\n{d['Data Domain']} -> {d['Family']}")
    print(f"Reason: {d['Why']}")

with open("lab1_2_try.json", "w") as f:
    json.dump(data, f, indent=2)
print("\nSaved lab1_2_try.json")