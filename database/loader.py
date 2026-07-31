import json

with open("drug_info.json", "r", encoding="utf-8") as f:
    DRUGS = json.load(f)

# قاموس: الاسم → DrugBank ID
NAME_TO_ID = {}

# قاموس: DrugBank ID → الاسم
ID_TO_NAME = {}

for drug_id, info in DRUGS.items():

    name = info.get("name", "").strip()

    if name:
        NAME_TO_ID[name.lower()] = drug_id
        ID_TO_NAME[drug_id] = name
