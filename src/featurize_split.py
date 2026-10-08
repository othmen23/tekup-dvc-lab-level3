import os
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

p = yaml.safe_load(open("params.yaml"))["featurize"]
df = pd.read_csv("data/interim/wine_clean.csv")

# features
df["is_red"] = (df["color"] == "red").astype(int)
df["so2_ratio"] = df["free sulfur dioxide"] / df["total sulfur dioxide"]
df = df.drop(columns="color")
num_cols = [c for c in df.columns if c not in ("quality", "is_red")]
df[num_cols] = (df[num_cols] - df[num_cols].mean()) / df[num_cols].std()

# target: good wine if quality >= threshold
df["target"] = (df["quality"] >= p["good_threshold"]).astype(int)
df = df.drop(columns="quality")

train, test = train_test_split(
    df, test_size=p["test_size"], random_state=p["seed"], stratify=df["target"]
)

os.makedirs("data/processed", exist_ok=True)
train.to_csv("data/processed/train.csv", index=False)
test.to_csv("data/processed/test.csv", index=False)
print("train/test:", train.shape, test.shape, "| good wines:", round(df["target"].mean(), 3))