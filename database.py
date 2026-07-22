import os
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
XML_PATH = "full database.xml"

# ==========================================================
# LOAD JSON FILES
# ==========================================================

if os.path.exists(DRUG_INFO_PATH):

    with open(DRUG_INFO_PATH, "r", encoding="utf-8") as f:
        drug_info = json.load(f)

else:

    print("WARNING: drug_info.json not found.")
    drug_info = {}

if os.path.exists(SYNONYMS_PATH):

    with open(SYNONYMS_PATH, "r", encoding="utf-8") as f:
        drug_synonyms = json.load(f)

else:

    print("WARNING: drugs_synonyms.json not found.")
    drug_synonyms = {}

# ==========================================================
# LOAD INTERACTION TABLE
# ==========================================================

if os.path.exists(INTERACTION_PATH):

    interaction_df = pd.read_csv(INTERACTION_PATH)

else:

    print("WARNING: all_id_interaction.csv not found.")

    interaction_df = pd.DataFrame(
        columns=[
            "Drug1",
            "Drug2",
            "Interaction",
            "Adverse Effects"
        ]
    )

# ==========================================================
# LOAD LABELS
# ==========================================================

if os.path.exists(LABEL_PATH):

    label_df = pd.read_excel(LABEL_PATH)

else:

    print("WARNING: interaction_counts_4.xlsx not found.")
    label_df = pd.DataFrame()

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

print(f"Drug Registry Loaded: {len(drug_registry)} drugs")

# ==========================================================
# Search Index
# ==========================================================

search_index = defaultdict(set)

for drug_id, drug in drug_registry.items():

    if drug.get("name"):
        search_index[drug["name"].lower()].add(drug_id)

    for syn in drug.get("synonyms", []):

        if syn:
            search_index[syn.lower()].add(drug_id)

print(f"Search Index Loaded: {len(search_index)} entries")

# ==========================================================
# DDI Lookup
# ==========================================================

ddi_lookup = defaultdict(list)

try:

    interaction_df = pd.read_csv(INTERACTION_PATH)

    for _, row in interaction_df.iterrows():

        key = frozenset([
            str(row["Drug1"]).replace("Compound::", ""),
            str(row["Drug2"]).replace("Compound::", "")
        ])

        ddi_lookup[key].append({

            "drug1": str(row["Drug1"]).replace("Compound::", ""),
            "drug2": str(row["Drug2"]).replace("Compound::", ""),
            "interaction": row["Interaction"],
            "adverse_effects":
                None if pd.isna(row["Adverse Effects"])
                else row["Adverse Effects"]

        })

    print(f"Loaded {len(ddi_lookup)} drug interactions.")

except Exception as e:

    print("WARNING: all_id_interaction.csv could not be loaded.")
    print(e)

    ddi_lookup = defaultdict(list)

# ==========================================================
# Food Interactions
# ==========================================================

food_interactions = {}

print("Food interactions skipped (XML file not available).")

