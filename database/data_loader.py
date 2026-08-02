import pandas as pd
import streamlit as st


@st.cache_data
def load_drug_lookup():
    """
    Load DrugBank lookup table.

    Returns:
        NAME_TO_ID : dict
        ID_TO_NAME : dict
        DRUG_INFO  : dict
    """

    df = pd.read_csv("drug_lookup.csv")

    df["drug_name"] = df["drug_name"].astype(str).str.strip()

    name_to_id = dict(zip(df["drug_name"], df["drug_id"]))
    id_to_name = dict(zip(df["drug_id"], df["drug_name"]))

    drug_info = (
        df.set_index("drug_id")
        .to_dict(orient="index")
    )

    return name_to_id, id_to_name, drug_info


NAME_TO_ID, ID_TO_NAME, DRUG_INFO = load_drug_lookup()
