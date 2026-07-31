import sqlite3
import zipfile
from pathlib import Path

# File path configuration
DB_FILE = Path("all_id_interaction.db")
ZIP_FILE = Path("all_id_interaction.zip")


def get_connection():
    """
    Establishes a secure connection to the SQLite database.
    Automatically extracts the ZIP file if the database does not exist.
    """
    if not DB_FILE.exists():
        with zipfile.ZipFile(ZIP_FILE, "r") as z:
            z.extractall(".")

    conn = sqlite3.connect(DB_FILE)
    # Enable row_factory to access columns by name instead of numerical indexes
    conn.row_factory = sqlite3.Row

    return conn


def get_interaction(drug1_id, drug2_id):
    """
    Performs a bidirectional search for drug-drug interactions using IDs.
    Checks both combinations (Drug1 to Drug2) and (Drug2 to Drug1) to ensure accuracy.
    """
    conn = get_connection()

    # Parameterized SQL query to safely fetch the first matching interaction row
    row = conn.execute(
        """
        SELECT *
        FROM interactions
        WHERE 
            ("Drug1 ID" = ? AND "Drug2 ID" = ?)
            OR 
            ("Drug1 ID" = ? AND "Drug2 ID" = ?)
        LIMIT 1;
        """,
        (
            drug1_id,
            drug2_id,
            drug2_id,
            drug1_id
        )
    ).fetchone()

    # Close the connection immediately to free system resources
    conn.close()

    return row
