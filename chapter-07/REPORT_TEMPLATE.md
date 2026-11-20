# MongoDB Experiment 7 Report

**Student name:** [Your name]  
**Student ID:** [Your ID]  
**Course/section:** [Your course]  
**Date performed:** [Date]

## Lab 7.1 — Analyze a Production-Style Schema

### Objective
Examine document modelling choices, compare embedding and referencing, measure BSON document sizes, and understand the 16 MiB BSON document limit.

### Procedure
1. Started MongoDB using Docker Compose.
2. Ran `python lab7_1/schema_analysis.py`.
3. Recorded the inserted document counts and BSON sizes printed by the script.
4. Compared when embedding and referencing are appropriate.

### Results
Paste your actual terminal output and add your screenshots here.

### Discussion
Explain which fields could be embedded when they are small and bounded, and which relationships should be referenced when records are shared or independently updated.

## Lab 7.2 — Working Set Analysis

### Objective
Create a 100,000-document workload and examine random-read latency and WiredTiger cache metrics.

### Procedure
1. Ran `python lab7_2/generate_workload.py` and confirmed the collection recreation prompt.
2. Ran `python lab7_2/random_reads.py --reads 5000`.
3. Ran `python lab7_2/cache_monitor.py --samples 5 --interval 10`.
4. Saved the actual JSON results from the `results` folder.

### Results
Paste your actual benchmark output, cache samples, and screenshots here.

### Discussion
Discuss measured read latency, throughput, cache changes, and any limitations. Do not claim cache pressure or performance improvement unless your measurements show it.

## Conclusion
Summarize what your own results demonstrate about schema design, document size, random reads, and cache monitoring.
