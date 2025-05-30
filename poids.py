import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

def run():
    st.title("Suivi du poids")

    conn = st.connection("gsheets", type=GSheetsConnection)

    # Charger l'historique des poids depuis l'onglet "poids"
    df_poids = conn.read(worksheet="poids", usecols=["date", "valeur"])
    if df_poids is None or df_poids.empty:
        df_poids = pd.DataFrame(columns=["date", "valeur"])

    # Formulaire pour ajouter un nouveau poids
    with st.form("formulaire_poids"):
        poids = st.number_input("Renseigne ton poids (kg)", min_value=0.0, step=0.1, format="%.1f")
        bouton = st.form_submit_button("Enregistrer")

        if bouton and poids > 0:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            nouvelle_ligne = {"date": date, "valeur": poids}
            # Ajouter la nouvelle ligne au DataFrame
            df_poids = pd.concat([df_poids, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
            # Réécrire toute la feuille Google Sheets
            conn.update(worksheet="poids", data=df_poids)
            st.success(f"Poids de {poids} kg enregistré le {date}")
            st.cache_data.clear()
            st.rerun()

    st.subheader("Historique des poids")
    if not df_poids.empty:
        st.dataframe(
            df_poids.rename(columns={"date": "Date", "valeur": "Poids (kg)"}).sort_values("Date", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Aucune donnée enregistrée pour le moment.")
