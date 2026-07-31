"""
RxShield Configuration
----------------------
Central configuration file for project paths and settings.
"""

from pathlib import Path

# ==========================
# Project Root
# ==========================

BASE_DIR = Path(__file__).resolve().parent

# ==========================
# Raw Data Sources
# ==========================

DRUG_DATABASE = BASE_DIR / "all_id_interaction.db"

DRUG_INFO = BASE_DIR / "drug_info.json"

DRUG_SYNONYMS = BASE_DIR / "drugs_synonyms.json"

FOOD_INTERACTIONS = BASE_DIR / "Drug to Food interactions Dataset.json"

# ==========================
# Application Settings
# ==========================

APP_NAME = "RxShield"

VERSION = "1.0.0"

CACHE_SIZE = 10000
