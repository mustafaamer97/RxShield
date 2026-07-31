import sqlite3
import zipfile
from pathlib import Path

DB_FILE = Path("all_id_interaction.db")
ZIP_FILE = Path("all_id_interaction.zip")


def get_connection():

    if not DB_FILE.exists():

        with zipfile.ZipFile(ZIP_FILE, "r") as z:
            z.extractall(".")

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row

    return conn
    def get_interaction(drug1_id, drug2_id):

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM interactions
        WHERE
        ("Drug1 ID"=? AND "Drug2 ID"=?)
        OR
        ("Drug1 ID"=? AND "Drug2 ID"=?)
        LIMIT 1
        """,
        (
            drug1_id,
            drug2_id,
            drug2_id,
            drug1_id
        )
    ).fetchone()

    conn.close()

    return row
