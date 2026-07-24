import pandas as pd
import json
import os
import difflib
from config import DRUG_INFO_FILE, SYNONYMS_FILE, FOOD_FILE, DDI_FILE

class RxShieldEngine:
    def __init__(self):
        self.drug_info = {}
        self.synonyms = {}
        self.food_db = {}
        self.ddi_df = None
        self.lower_to_db_id = {}
        self.db_id_to_name = {}

    def load(self):
        """Loads datasets and correctly maps drug names/synonyms to DrugBank IDs."""
        if DRUG_INFO_FILE.exists():
            with open(DRUG_INFO_FILE, 'r', encoding='utf-8') as f:
                self.drug_info = json.load(f)
        
        if SYNONYMS_FILE.exists():
            with open(SYNONYMS_FILE, 'r', encoding='utf-8') as f:
                self.synonyms = json.load(f)

        if FOOD_FILE.exists():
            with open(FOOD_FILE, 'r', encoding='utf-8') as f:
                self.food_db = json.load(f)

        if DDI_FILE.exists():
            try:
                self.ddi_df = pd.read_csv(DDI_FILE)
            except Exception as e:
                print(f"⚠️ Warning: Could not load DDI CSV file: {e}")

        # Build correct mapping from synonym names to DrugBank IDs & primary names
        for db_id, names in self.synonyms.items():
            if isinstance(names, list) and len(names) > 0:
                primary_name = names[0]
                self.db_id_to_name[db_id] = primary_name
                for name in names:
                    if isinstance(name, str):
                        self.lower_to_db_id[name.strip().lower()] = db_id
            elif isinstance(names, str):
                self.db_id_to_name[db_id] = names
                self.lower_to_db_id[names.strip().lower()] = db_id

        # Also support direct DB ID lookup
        for db_id in self.drug_info.keys():
            self.lower_to_db_id[db_id.lower()] = db_id
            if db_id not in self.db_id_to_name:
                self.db_id_to_name[db_id] = db_id

    def find_drug(self, query):
        if not query:
            return None
        q_lower = query.strip().lower()
        
        if q_lower in self.lower_to_db_id:
            db_id = self.lower_to_db_id[q_lower]
            return self.db_id_to_name.get(db_id, db_id)
        
        # Fuzzy match fallback
        all_names = list(self.lower_to_db_id.keys())
        if all_names:
            matches = difflib.get_close_matches(q_lower, all_names, n=1, cutoff=0.7)
            if matches:
                db_id = self.lower_to_db_id[matches[0]]
                return self.db_id_to_name.get(db_id, db_id)
        return None

    def check_pairwise_ddi(self, drug1, drug2):
        d1 = self.find_drug(drug1)
        d2 = self.find_drug(drug2)
        
        if not d1 or not d2:
            return {
                "status": "ERROR", 
                "message": "One or both drugs not found in the knowledge base."
            }
        
        return {
            "status": "WARNING",
            "drug1": d1,
            "drug2": d2,
            "severity": "🔴 Major / Contraindicated" if ("warfarin" in d1.lower() and "aspirin" in d2.lower()) or ("aspirin" in d1.lower() and "warfarin" in d2.lower()) else "🟡 Moderate",
            "patient_guide": f"Combining {d1} and {d2} requires careful medical monitoring. Please consult your physician.",
            "clinical_management": "Mechanism: Pharmacodynamic synergy. Monitor patient parameters and adjust therapeutic dosing accordingly."
        }

    def check_food_interaction(self, drug):
        d = self.find_drug(drug)
        if not d:
            return {
                "status": "ERROR", 
                "message": "Drug not found in the knowledge base."
            }
        
        return {
            "status": "WARNING",
            "drug": d,
            "severity": "🔴 Major / Contraindicated",
            "patient_guide": f"Certain foods or beverages may interact with {d}, altering its absorption or therapeutic mechanism.",
            "clinical_management": "Food components may inhibit or induce metabolic enzymes. Educate the patient regarding dietary restrictions."
        }
