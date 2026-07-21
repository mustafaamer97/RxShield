# ==========================================================
# RxShield Drug Registry
# ==========================================================

drug_registry = {}

for drug_id, info in drug_info.items():

    drug_registry[drug_id] = {

        "id": drug_id,

        "name": info.get("name"),

        "description": info.get("description"),

        "formula": info.get("formula"),

        "smiles": info.get("smiles"),

        "synonyms": drug_synonyms.get(drug_id, [])

    }

print("=" * 60)
print("Drug Registry:", len(drug_registry))
print("=" * 60)

sample = next(iter(drug_registry))
print(drug_registry[sample])from collections import defaultdict

search_index = defaultdict(set)

for drug_id, drug in drug_registry.items():

    # الاسم الأساسي
    if drug["name"]:
        search_index[drug["name"].lower()].add(drug_id)

    # المرادفات
    for syn in drug["synonyms"]:
        if syn:
            search_index[syn.lower()].add(drug_id)

print("=" * 60)
print("Search Index:", len(search_index))
print("=" * 60)

# اختبار
print(search_index["warfarin"])lections import defaultdict
from tqdm import tqdm
import pandas as pd

ddi_lookup = defaultdict(list)

for _, row in tqdm(interaction_df.iterrows(), total=len(interaction_df)):

    key = frozenset([
        row["Drug1"].replace("Compound::", ""),
        row["Drug2"].replace("Compound::", "")
    ])

    ddi_lookup[key].append({

        "drug1": row["Drug1"].replace("Compound::", ""),
        "drug2": row["Drug2"].replace("Compound::", ""),
        "interaction": row["Interaction"],
        "adverse_effects": (
            None if pd.isna(row["Adverse Effects"])
            else row["Adverse Effects"]
        )

    })

print("=" * 60)
print("DDI Lookup:", len(ddi_lookup))
print("=" * 60)from tqdm import tqdm

food_interactions = {}

for drug in tqdm(drugs):

    # DrugBank ID
    ids = drug.xpath('./*[local-name()="drugbank-id"][@primary="true"]')
    if not ids:
        continue

    drug_id = ids[0].text

    # Drug name
    names = drug.xpath('./*[local-name()="name"]')
    drug_name = names[0].text if names else None

    # Food interactions
    foods = drug.xpath('./*[local-name()="food-interactions"]/*[local-name()="food-interaction"]')

    food_list = []

    for food in foods:
        if food.text:
            food_list.append(food.text.strip())

    if food_list:
        food_interactions[drug_id] = {
            "drug_name": drug_name,
            "food_interactions": food_list
        }

print("=" * 60)
print("Drugs with food interactions:", len(food_interactions))
print("=" * 60)
