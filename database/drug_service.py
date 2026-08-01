import pandas as pd

df = pd.read_csv("drug_data.csv")

df = df.dropna(subset=["name"])

df["name"] = df["name"].astype(str)

DRUG_NAMES = sorted(df["name"].tolist())

NAME_TO_ID = dict(zip(df["name"], df["drug-id"]))

ID_TO_NAME = dict(zip(df["drug-id"], df["name"]))
