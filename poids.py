import streamlit as st
import sqlite3
from datetime import datetime

def run():
    conn = sqlite3.connect('suivi_forme.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS poids (
            date TEXT,
            valeur REAL
        )
    ''')
    conn.commit()

    st.title("Suivi du poids")

    with st.form("formulaire_poids"):
        poids = st.number_input("Renseigne ton poids (kg)", min_value=0.0, step=0.1, format="%.1f")
        bouton = st.form_submit_button("Enregistrer")

        if bouton and poids > 0:
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO poids (date, valeur) VALUES (?, ?)", (date, poids))
            conn.commit()
            st.success(f"Poids de {poids} kg enregistré le {date}")

    st.subheader("Historique des poids")
    c.execute("SELECT date, valeur FROM poids ORDER BY date DESC")
    lignes = c.fetchall()

    if lignes:
        st.dataframe(
            [{"Date": date, "Poids (kg)": valeur} for date, valeur in lignes],
            use_container_width=True
        )
    else:
        st.info("Aucune donnée enregistrée pour le moment.")

    conn.close()