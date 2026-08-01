import pandas as pd
import streamlit as st

df = pd.read_csv("drug_data.csv")

st.write("Columns:")
st.write(df.columns.tolist())

st.write("Shape:")
st.write(df.shape)

st.write("First 10 rows:")
st.dataframe(df.head(10))
