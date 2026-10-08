import json
import sys

m = json.load(open("metrics/metrics.json"))
print("f1_score:", m["f1_score"])
sys.exit(0 if m["f1_score"] >= 0.35 else 1)
