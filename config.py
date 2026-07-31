from pathlib import Path

# ===============================
# Project Paths
# ===============================

BASE_DIR = Path(__file__).resolve().parent

# Raw Data Files
DRUG_INFO_FILE = BASE_DIR / "drug_info.json"
DRUG_SYNONYMS_FILE = BASE_DIR / "drugs_synonyms.json"
DDI_DATABASE_ZIP = BASE_DIR / "all_id_interaction.zip"
DFI_DATASET_FILE = BASE_DIR / "Drug to Food interactions Dataset.json"
INTERACTION_DATASET = BASE_DIR / "data_final_v5.zip"

# SQLite Database
DATABASE_FILE = BASE_DIR / "rxshield.db"
