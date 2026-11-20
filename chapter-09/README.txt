MongoDB Labs 9.1 and 9.2 — runnable files
==========================================

Files
-----
Activity-9.1/lab9_1.py
  Measures total elapsed time and average latency for 1,000 sequential inserts
  under six configurations: w=1/majority/3, each with j=true and j=false.
  Writes measured results to lab9_1_results.csv and lab9_1_output.txt.

Activity-9.2/lab9_2_partition_observer.py
  Continuously records replica-set state and attempts w=1 and w=majority writes.
  Writes actual observations to lab9_2_partition_observations.csv and
  lab9_2_output.txt.

IMPORTANT TECHNICAL NOTE
------------------------
MongoDB's built-in write concern does not define w="all". For a replica set with
three DATA-BEARING members, w=3 is the correct way to wait for all three. If your
replica set has only two data-bearing nodes plus an arbiter, do not use w=3:
an arbiter cannot acknowledge application writes. Use the actual data-bearing
member count instead.

Run scripts where Docker replica-set member names resolve. For the recent lab
setup, this can be a Python container on network activity-81-clean_default.
The URI defaults target lab81-mongo1/2/3; if your actual replica-set member names
are mongo1/mongo2/mongo3, set MONGO_URI to the corresponding URI.

Example PowerShell: build a small Python image in Activity-9.1 / Activity-9.2
---------------------------------------------------------------------------
Create a Dockerfile with:
  FROM python:3.12-slim
  WORKDIR /app
  RUN pip install --no-cache-dir pymongo
  COPY . /app
  CMD ["python", "lab9_1.py"]

Then build/run from the folder, mounting it into the shared Docker network.
For Lab 9.1:
  docker run --rm -it --network activity-81-clean_default `
    -v "${PWD}:/app" -w /app lab9-python python lab9_1.py

For Lab 9.2, use the same pattern but replace the final script name with
lab9_2_partition_observer.py. If using the other replica-set network, replace
activity-81-clean_default with the network shown by:
  docker network ls

Lab 9.2 partition procedure
---------------------------
1. Verify the replica set is healthy and identify a SECONDARY:
   docker exec lab81-mongo1 mongosh --quiet --eval "rs.status().members.map(m=>({name:m.name,state:m.stateStr,health:m.health}))"
2. In one terminal, run the observer.
3. In another PowerShell terminal, inspect network/container names:
   docker network ls
   docker inspect lab81-mongo2 --format '{{json .NetworkSettings.Networks}}'
4. Disconnect only the selected secondary from the replica-set Docker network:
   docker network disconnect activity-81-clean_default lab81-mongo2
5. Observe results. With one of three data-bearing nodes disconnected, w=1 and
   w=majority may both succeed because primary + one secondary still form a
   majority. Reconnect the secondary after the experiment:
   docker network connect activity-81-clean_default lab81-mongo2
6. To test loss of majority, isolate the OTHER secondary too, but only after
   recording the first phase. w=majority can time out; the primary may step down
   after it loses contact with a majority. w=1 may succeed only while a primary
   remains writable. Do not describe the node as guaranteed "read-only"; once it
   steps down, it is no longer primary and cannot accept normal primary writes.
7. Reconnect all isolated members and wait for healthy status before stopping.

Safety:
- This is a local lab procedure only. Never disconnect production replica-set
  networks.
- Docker network disconnect is reversible, but verify the exact network and
  container names first.
- Do not run disconnect commands on a PRIMARY.
- Exact timings and outcomes depend on election timeout, write timeout, priorities,
  and the current replica-set configuration. Use the actual generated CSV/text
  files as evidence; do not invent results.
