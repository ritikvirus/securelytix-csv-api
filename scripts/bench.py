import time, subprocess, statistics, sys, json, os, csv, io, requests, pathlib, random, tempfile

CSV = tempfile.NamedTemporaryFile(delete=False, suffix=".csv").name
subprocess.run(["python", "scripts/make_fake_csv.py", "100000"], stdout=open(CSV, "w"), check=True)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
latencies = []
for _ in range(N):
    t0 = time.time()
    r = requests.post("http://localhost/upload", files={"file": open(CSV, "rb")})
    latencies.append(r.json()["insert_latency_ms"])
print("runs:", latencies)
print("p50:", statistics.median(latencies), "ms", "max:", max(latencies))
