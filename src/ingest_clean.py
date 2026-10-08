# Ingestion
import os
import pandas as pd

red = pd.read_csv("data/raw/winequality-red.csv", sep=";")
white = pd.read_csv("data/raw/winequality-white.csv", sep=";")
red["color"] = "red"
white["color"] = "white"
df = pd.concat([red, white], ignore_index=True)

n_before = len(df)
df = df.drop_duplicates().reset_index(drop=True)
print(f"rows: {n_before} -> {len(df)} ({n_before - len(df)} duplicates removed)")

# consistency checks
assert df.isna().sum().sum() == 0, "missing values found"
assert df["quality"].between(0, 10).all(), "quality out of range"
assert df["pH"].between(0, 14).all(), "pH out of range"
assert (df["alcohol"] > 0).all(), "non-positive alcohol"
assert set(df["color"]) == {"red", "white"}, "unexpected color values"

os.makedirs("data/interim", exist_ok=True)
df.to_csv("data/interim/wine_clean.csv", index=False)