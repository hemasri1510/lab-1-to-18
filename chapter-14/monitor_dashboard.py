import time
from pymongo import MongoClient
from datetime import datetime

uri = "mongodb://admin:password123@mongo1:27017,mongo2:27017,mongo3:27017/?replicaSet=rs0&authSource=admin"
client = MongoClient(uri, serverSelectionTimeoutMS=5000)

print("Connected to MongoDB - Monitoring started... (Ctrl+C to stop)")

while True:
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = client.admin.command('serverStatus')
        repl = client.admin.command('replSetGetStatus')

        # 1. Connections
        conn = status['connections']['current']

        # 2. Opcounters
        ops = status['opcounters']
        op_str = f"insert:{ops['insert']} query:{ops['query']} update:{ops['update']} delete:{ops['delete']}"

        # 3. WiredTiger Cache
        cache = status['wiredTiger']['cache']
        pages_requested = cache.get('pages requested from the cache', 0)
        pages_read = cache.get('pages read into cache', 0)
        # hit ratio = 1 - (pages read from disk / pages requested)
        hit_ratio = ((pages_requested - pages_read) / pages_requested * 100) if pages_requested > 0 else 100.0

        # 4. Replication Lag
        members = repl['members']
        primary_optime = None
        max_lag = 0
        for m in members:
            if m['stateStr'] == 'PRIMARY':
                primary_optime = m['optime']['ts'].time
        for m in members:
            if m['stateStr'] == 'SECONDARY':
                lag = primary_optime - m['optime']['ts'].time
                max_lag = max(max_lag, lag)

        # Format as table
        line = f"[{now}] Conn: {conn} | Ops: {op_str} | Cache Hit: {hit_ratio:.1f}% | Max Lag: {max_lag}s"
        print(line)

        # Write to log file
        with open('metrics.log', 'a') as f:
            f.write(line + "\n")

        # Threshold Alerting
        if hit_ratio < 80:
            print(f"⚠️ WARNING: Cache hit ratio low: {hit_ratio:.1f}% (< 80%)")
        if max_lag > 10:
            print(f"⚠️ WARNING: Replication lag high: {max_lag}s (> 10s)")

        time.sleep(30)

    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
        break
    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)