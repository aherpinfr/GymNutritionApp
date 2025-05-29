import streamlit as st
from streamlit_gsheets import GSheetsConnection

conn = st.connection("gsheets", type=GSheetsConnection)
df_nutrition = conn.read(worksheet="nutrition")
st.dataframe(df_nutrition)
