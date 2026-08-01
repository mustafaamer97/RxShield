import pandas as pd

df = pd.read_csv("drug_data.csv")

df = df.dropna(subset=["drug-id", "name"])

df["drug-id"] = df["drug-id"].astype(str)
df["name"] = df["name"].astype(str).str.strip()

DRUG_NAMES = sorted(df["name"].unique())

NAME_TO_ID = dict(zip(df["name"], df["drug-id"]))
ID_TO_NAME = dict(zip(df["drug-id"], df["name"]))
