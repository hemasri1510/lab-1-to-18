# MongoDB Experiment 7 — Production Schema & Working Set Analysis

This project provides runnable activities for:
- **Lab 7.1:** Analyze a production-style threat-intelligence schema, compare embedding and referencing, measure BSON document sizes, and demonstrate the 16 MB document limit safely.
- **Lab 7.2:** Generate a 100,000-document workload (~2 KB/document), measure random-read performance, and record WiredTiger cache statistics.

## Requirements
- Docker Desktop running (Linux containers)
- Python 3.10+
- Python packages: `pymongo`, `streamlit`, `pandas`

Install Python packages from the project root:
```powershell
python -m pip install -r requirements.txt
```

Start MongoDB:
```powershell
docker compose up -d
```

Check the connection:
```powershell
python scripts/check_connection.py
```

Run Lab 7.1:
```powershell
python lab7_1/schema_analysis.py
```

Run Lab 7.2 workload creation (creates/refreshes the `working_set` collection):
```powershell
python lab7_2/generate_workload.py
```

Run random-read benchmark:
```powershell
python lab7_2/random_reads.py --reads 5000
```

Capture cache stats:
```powershell
python lab7_2/cache_monitor.py --samples 5 --interval 10
```

Optional dashboard:
```powershell
streamlit run dashboard.py
```

## Notes
- These scripts report **your actual local run results**. Do not copy example metrics from another report.
- The workload generator drops only the `working_set` collection before recreating it; review the code before running.
- The 16 MB limit demo is intentionally non-destructive: it calculates BSON sizes locally and does not attempt to insert an oversized document.
- Stop MongoDB when finished with `docker compose down`. Do not add `-v` unless you intentionally want to delete the stored volume data.
