# Evaluation script v2
# Evaluation script
import json
import os
import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score

model = joblib.load("models/model.pkl")
test = pd.read_csv("data/processed/test.csv")

X = test.drop(columns="target")
y = test["target"]
pred = model.predict(X)

os.makedirs("metrics", exist_ok=True)
with open("metrics/metrics.json", "w") as f:
    json.dump(
        {"accuracy": accuracy_score(y, pred), "f1_score": f1_score(y, pred)},
        f,
        indent=2,
    )