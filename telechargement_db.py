import streamlit as st
import pandas as pd
import json
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

def get_next_id(df):
    if df.empty or 'id' not in df.columns or df['id'].isnull().all():
        return 1
    else:
        return int(df['id'].max()) + 1

def run():
    st.title("Suivi Gym")

    # Connexion Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Lecture des données existantes
    df_exercices = conn.read(worksheet="exercices", usecols=["id", "nom", "parametres"])
    if df_exercices is None or df_exercices.empty:
        df_exercices = pd.DataFrame(columns=["id", "nom", "parametres"])

    df_perf = conn.read(worksheet="performances", usecols=["id", "exercice_id", "date", "donnees"])
    if df_perf is None or df_perf.empty:
        df_perf = pd.DataFrame(columns=["id", "exercice_id", "date", "donnees"])

    # Sommaire cliquable
    st.markdown("""
    <h3>Sommaire</h3>
    <ul>
        <li><a href="#ajouter-un-exercice">Ajouter un exercice</a></li>
        <li><a href="#supprimer-un-exercice">Supprimer un exercice</a></li>
        <li><a href="#enregistrer-une-performance">Enregistrer une performance</a></li>
        <li><a href="#historique-des-performances">Historique des performances</a></li>
    </ul>
    """, unsafe_allow_html=True)

    # --- Ajouter un exercice ---
    st.markdown("<h2 id='ajouter-un-exercice'>Ajouter un exercice</h2>", unsafe_allow_html=True)
    with st.form("ajout_exercice"):
        nom_ex = st.text_input("Nom de l'exercice (ex : Elliptique, Développé couché, etc.)")
        parametres = st.text_area("Paramètres à suivre (séparés par des virgules, ex : km, durée, calories)")
        bouton_ex = st.form_submit_button("Ajouter l'exercice")
        if bouton_ex and nom_ex and parametres:
            new_id = get_next_id(df_exercices)
            nouvelle_ligne = {"id": new_id, "nom": nom_ex, "parametres": parametres}
            conn.append(worksheet="exercices", data=[nouvelle_ligne])
            st.success(f"Exercice '{nom_ex}' ajouté avec les paramètres : {parametres}")
            st.experimental_rerun()

    # --- Supprimer un exercice ---
    st.markdown("<h2 id='supprimer-un-exercice'>Supprimer un exercice</h2>", unsafe_allow_html=True)
    if not df_exercices.empty:
        ex_supp_dict = {f"{row['nom']} ({row['parametres']})": row['id'] for _, row in df_exercices.iterrows()}
        ex_supp_choix = st.selectbox("Sélectionne un exercice à supprimer", list(ex_supp_dict.keys()))
        if st.button("Supprimer cet exercice"):
            ex_id_to_del = ex_supp_dict[ex_supp_choix]
            # Supprimer l'exercice et ses performances associées
            df_exercices = df_exercices[df_exercices['id'] != ex_id_to_del]
            df_perf = df_perf[df_perf['exercice_id'] != ex_id_to_del]
            conn.update(worksheet="exercices", data=df_exercices)
            conn.update(worksheet="performances", data=df_perf)
            st.success(f"Exercice '{ex_supp_choix}' et ses performances associées supprimés.")
            st.experimental_rerun()
    else:
        st.info("Aucun exercice créé pour le moment.")

    # --- Enregistrer une performance ---
    st.markdown("<h2 id='enregistrer-une-performance'>Enregistrer une performance</h2>", unsafe_allow_html=True)
    if not df_exercices.empty:
        ex_options = {f"{row['nom']} ({row['parametres']})": (row['id'], row['parametres']) for _, row in df_exercices.iterrows()}
        choix = st.selectbox("Choisis un exercice", list(ex_options.keys()))
        ex_id, params = ex_options[choix]
        params_list = [p.strip() for p in params.split(",")]

        with st.form("ajout_performance"):
            valeurs = {}
            for param in params_list:
                valeurs[param] = st.text_input(f"{param}")
            bouton_perf = st.form_submit_button("Enregistrer la performance")
            if bouton_perf:
                date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_perf_id = get_next_id(df_perf)
                nouvelle_perf = {
                    "id": new_perf_id,
                    "exercice_id": ex_id,
                    "date": date_str,
                    "donnees": json.dumps(valeurs)
                }
                conn.append(worksheet="performances", data=[nouvelle_perf])
                st.success(f"Performance enregistrée pour {choix} le {date_str}")
                st.experimental_rerun()

        # --- Historique des performances ---
        st.markdown("<h2 id='historique-des-performances'>Historique des performances</h2>", unsafe_allow_html=True)
        perf_ex = df_perf[df_perf['exercice_id'] == ex_id]
        if not perf_ex.empty:
            perf_ex_sorted = perf_ex.sort_values("date", ascending=False)
            histo = []
            for _, row in perf_ex_sorted.iterrows():
                data = json.loads(row['donnees'])
                data["Date"] = row['date']
                histo.append(data)
            st.dataframe(histo, use_container_width=True)
        else:
            st.info("Aucune performance enregistrée pour cet exercice.")
    else:
        st.info("Aucun exercice créé pour le moment.")
