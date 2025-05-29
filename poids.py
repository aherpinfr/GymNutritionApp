import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

def run():
    st.title("Suivi du poids")

    # Connexion à Google Sheets (utilise le nom défini dans secrets.toml)
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
            # Ajout de la nouvelle ligne dans Google Sheets
            nouvelle_ligne = {"date": date, "valeur": poids}
            conn.append(worksheet="poids", data=[nouvelle_ligne])
            st.success(f"Poids de {poids} kg enregistré le {date}")
            st.rerun()  # Recharge la page pour afficher la nouvelle donnée

    st.subheader("Historique des poids")
    if not df_poids.empty:
        # Affichage du DataFrame
        st.dataframe(
            df_poids.rename(columns={"date": "Date", "valeur": "Poids (kg)"}).sort_values("Date", ascending=False),
            use_container_width=True
        )
    else:
        st.info("Aucune donnée enregistrée pour le moment.")
