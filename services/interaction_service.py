import pandas as pd
from itertools import combinations


def get_single_drug_interactions(db_conn, drug_id):
    """
    Return all interactions involving a single drug.
    """
    return pd.read_sql_query(
        """
        SELECT *
        FROM interactions
        WHERE "Drug1 ID" = ?
           OR "Drug2 ID" = ?
        """,
        db_conn,
        params=(drug_id, drug_id),
    )


def get_pair_interaction(db_conn, drug_a, drug_b):
    """
    Return the interaction between two drugs.
    """
    return pd.read_sql_query(
        """
        SELECT *
        FROM interactions
        WHERE ("Drug1 ID"=? AND "Drug2 ID"=?)
           OR ("Drug1 ID"=? AND "Drug2 ID"=?)
        """,
        db_conn,
        params=(drug_a, drug_b, drug_b, drug_a),
    )


def get_regimen_pairs(selected_regimen):
    """
    Generate all unique drug pairs.
    """
    return list(combinations(selected_regimen, 2))
