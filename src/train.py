import os
import joblib
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier

p = yaml.safe_load(open("params.yaml"))["train"]
train = pd.read_csv("data/processed/train.csv")

X = train.drop(columns="target")
y = train["target"]

model = RandomForestClassifier(
    n_estimators=p["n_estimators"],
    max_depth=p["max_depth"],
    random_state=p["seed"],
)
model.fit(X, y)

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/model.pkl")