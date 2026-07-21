# ==========================================================
# Interaction Lookup
# ==========================================================

def find_interaction(drug1_id, drug2_id):
    key = frozenset([drug1_id, drug2_id])
    return ddi_lookup.get(key, [])


# ==========================================================
# Resolve Drug Name -> DrugBank ID
# ==========================================================

def resolve_drug(query):
    query = query.strip().lower()

    # Exact match
    if query in search_index:
        return next(iter(search_index[query]))

    # Partial match
    for key in search_index.keys():
        if query in key:
            return next(iter(search_index[key]))

    return None


# ==========================================================
# Clinical Metadata
# ==========================================================

def get_clinical_metadata(interaction_text):

    text = interaction_text.lower()

    for keyword, metadata in clinical_rules.items():
        if keyword in text:
            return metadata

    return {
        "severity": "Unknown",
        "mechanism": "Unknown",
        "evidence": "Unknown",
        "clinical_management": "No recommendation available."
    }


# ==========================================================
# RxShield Engine
# ==========================================================

def rxshield_engine(drug1_name, drug2_name):

    drug1_id = resolve_drug(drug1_name)
    drug2_id = resolve_drug(drug2_name)

    if drug1_id is None:
        return {"error": f"Drug not found: {drug1_name}"}

    if drug2_id is None:
        return {"error": f"Drug not found: {drug2_name}"}

    drug1 = drug_registry[drug1_id]
    drug2 = drug_registry[drug2_id]

    interactions = find_interaction(drug1_id, drug2_id)

    if not interactions:
        return {
            "drug1": drug1,
            "drug2": drug2,
            "interaction_found": False
        }

    interaction = interactions[0]

    metadata = get_clinical_metadata(interaction["interaction"])

    return {
        "interaction_found": True,
        "drug1": drug1,
        "drug2": drug2,
        "interaction": interaction["interaction"],
        "adverse_effects": interaction["adverse_effects"],
        "severity": metadata["severity"],
        "mechanism": metadata["mechanism"],
        "evidence": metadata["evidence"],
        "clinical_management": metadata["clinical_management"],
        "food1": food_interactions.get(drug1_id),
        "food2": food_interactions.get(drug2_id)
    }
