import sqlite3
import zipfile
from pathlib import Path
import streamlit as st

DB_FILE = Path("all_id_interaction.db")
ZIP_FILE = Path("all_id_interaction.zip")


@st.cache_resource
def get_connection():
    """
    Returns a cached SQLite connection.
    Automatically extracts the database if only the ZIP exists.
    """

    if not DB_FILE.exists():

        if ZIP_FILE.exists():
            with zipfile.ZipFile(ZIP_FILE, "r") as z:
                z.extractall(".")

        else:
            raise FileNotFoundError(
                "all_id_interaction.db or all_id_interaction.zip not found."
            )

    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row

    return conn


def get_interaction(drug1_id, drug2_id):
    """
    Search interaction in both directions.
    """

    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM interactions
        WHERE
        (
            "Drug1 ID" = ?
            AND
            "Drug2 ID" = ?
        )

        OR

        (
            "Drug1 ID" = ?
            AND
            "Drug2 ID" = ?
        )

        LIMIT 1
        """,
        (
            drug1_id,
            drug2_id,
            drug2_id,
            drug1_id,
        ),
    ).fetchone()

    return row
