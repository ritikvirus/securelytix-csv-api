#!/usr/bin/env python3
import csv, random, sys

rows = int(sys.argv[1]) if len(sys.argv) > 1 else 100000
writer = csv.writer(sys.stdout)
writer.writerow([f"col{i}" for i in range(1,11)])
for i in range(rows):
    writer.writerow([i] + [f"val{random.randint(1000,9999)}" for _ in range(9)])
