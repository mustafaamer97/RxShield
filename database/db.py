from pathlib import Path
import sqlite3
import zipfile


def get_database(zip_file, db_file):
    """
    Establishes a secure connection to a dynamic SQLite database.
    Automatically extracts the specified ZIP file if the database does not exist.
    """
    db_path = Path(db_file)

    if not db_path.exists():
        with zipfile.ZipFile(zip_file, "r") as z:
            z.extractall(".")

    conn = sqlite3.connect(db_path)
    # Enable row_factory to access columns by name instead of numerical indexes
    conn.row_factory = sqlite3.Row

    return conn


def get_interaction_connection():
    """Returns a connection setup for the interaction database."""
    return get_database(
        "all_id_interaction.zip",
        "all_id_interaction.db"
    )


def get_drug_connection():
    """Returns a connection setup for the modern v5 drug info database."""
    return get_database(
        "data_final_v5.zip",
        "data_final_v5.db"
    )


def get_interaction(drug1_id, drug2_id):
    """
    Performs a bidirectional search for drug-drug interactions using IDs.
    Checks both combinations (Drug1 to Drug2) and (Drug2 to Drug1) using the interaction connection.
    """
    # Use the refactored dynamic connection function
    conn = get_interaction_connection()

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
