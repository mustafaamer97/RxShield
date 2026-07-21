import json
import pandas as pd
from collections import defaultdict
from tqdm import tqdm
from lxml import etree

# ==========================================================
# PATHS
# ==========================================================

DRUG_INFO_PATH = "drug_info.json"
SYNONYMS_PATH = "drugs_synonyms.json"
INTERACTION_PATH = "all_id_interaction.csv"
LABEL_PATH = "interaction_counts_4.xlsx"

# إذا كان لديك ملف XML ضعه بنفس الاسم داخل المشروع
XML_PATH = "full database.xml"

# ==========================================================
# LOAD FILES
# ==========================================================

with open(DRUG_INFO_PATH, "r", encoding="utf-8") as f:
    drug_info = json.load(f)

with open(SYNONYMS_PATH, "r", encoding="utf-8") as f:
    drug_synonyms = json.load(f)

interaction_df = pd.read_csv(INTERACTION_PATH)
label_df = pd.read_excel(LABEL_PATH)

# ==========================================================
# Drug Registry
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

# ==========================================================
# Search Index
# ==========================================================

search_index = defaultdict(set)

for drug_id, drug in drug_registry.items():

    if drug["name"]:
        search_index[drug["name"].lower()].add(drug_id)

    for syn in drug["synonyms"]:
        if syn:
            search_index[syn.lower()].add(drug_id)

# ==========================================================
# DDI Lookup
# ==========================================================

ddi_lookup = defaultdict(list)

for _, row in interaction_df.iterrows():

    key = frozenset([
        row["Drug1"].replace("Compound::", ""),
        row["Drug2"].replace("Compound::", "")
    ])

    ddi_lookup[key].append({

        "drug1": row["Drug1"].replace("Compound::", ""),
        "drug2": row["Drug2"].replace("Compound::", ""),
        "interaction": row["Interaction"],
        "adverse_effects":
            None if pd.isna(row["Adverse Effects"])
            else row["Adverse Effects"]

    })

# ==========================================================
# Food Interactions
# ==========================================================

food_interactions = {}

try:

    parser = etree.XMLParser(remove_blank_text=True, huge_tree=True)

    tree = etree.parse(XML_PATH, parser)

    root = tree.getroot()

    drugs = root.xpath('./*[local-name()="drug"]')

    for drug in drugs:

        ids = drug.xpath('./*[local-name()="drugbank-id"][@primary="true"]')

        if not ids:
            continue

        drug_id = ids[0].text

        names = drug.xpath('./*[local-name()="name"]')
        drug_name = names[0].text if names else None

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

except Exception:
    # يعمل حتى لو لم يكن ملف XML موجودًا
    food_interactions = {}
