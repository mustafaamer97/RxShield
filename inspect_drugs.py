import streamlit as st
import pandas as pd

df = pd.read_csv("drug_data.csv")

st.write(df.head(20))

keywords = [
    "Aspirin",
    "Paracetamol",
    "Acetaminophen",
    "Metformin",
    "Warfarin",
    "Ibuprofen",
    "Amoxicillin",
    "Omeprazole",
]

st.subheader("Search Test")

for word in keywords:
    result = df[df["name"].str.contains(word, case=False, na=False)]

    st.write(f"### {word}")

    if len(result):
        st.write(result[["drug-id", "name"]].head())
    else:
        st.write("❌ Not Found")
