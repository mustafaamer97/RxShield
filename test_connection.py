from config import DRUG_DATABASE
from database.db_manager import DatabaseManager

db = DatabaseManager(DRUG_DATABASE)

tables = db.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
)

print(tables)

db.close()
