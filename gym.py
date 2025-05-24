import streamlit as st
import sqlite3
import json
from datetime import datetime

def run():
    conn = sqlite3.connect('suivi_forme.db')
    c = conn.cursor()

    # Création des tables (exercices et performances)
    c.execute('''
        CREATE TABLE IF NOT EXISTS exercices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT,
            parametres TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS performances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercice_id INTEGER,
            date TEXT,
            donnees TEXT,
            FOREIGN KEY(exercice_id) REFERENCES exercices(id)
        )
    ''')
    conn.commit()

    st.title("Suivi Gym")

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
            c.execute("INSERT INTO exercices (nom, parametres) VALUES (?, ?)", (nom_ex, parametres))
            conn.commit()
            st.success(f"Exercice '{nom_ex}' ajouté avec les paramètres : {parametres}")

    # --- Supprimer un exercice ---
    c.execute("SELECT id, nom, parametres FROM exercices")
    exercices = c.fetchall()

    st.markdown("<h2 id='supprimer-un-exercice'>Supprimer un exercice</h2>", unsafe_allow_html=True)
    if exercices:
        ex_supp_dict = {f"{nom} ({parametres})": ex_id for ex_id, nom, parametres in exercices}
        ex_supp_choix = st.selectbox("Sélectionne un exercice à supprimer", list(ex_supp_dict.keys()))
        if st.button("Supprimer cet exercice"):
            ex_id_to_del = ex_supp_dict[ex_supp_choix]
            c.execute("DELETE FROM performances WHERE exercice_id = ?", (ex_id_to_del,))
            c.execute("DELETE FROM exercices WHERE id = ?", (ex_id_to_del,))
            conn.commit()
            st.success(f"Exercice '{ex_supp_choix}' et ses performances associées supprimés.")
            st.experimental_rerun()
    else:
        st.info("Aucun exercice créé pour le moment.")

    # --- Enregistrer une performance ---
    st.markdown("<h2 id='enregistrer-une-performance'>Enregistrer une performance</h2>", unsafe_allow_html=True)
    if exercices:
        ex_options = {f"{nom} ({parametres})": (ex_id, parametres) for ex_id, nom, parametres in exercices}
        choix = st.selectbox("Choisis un exercice", list(ex_options.keys()))
        ex_id, params = ex_options[choix]
        params_list = [p.strip() for p in params.split(",")]

        with st.form("ajout_performance"):
            valeurs = {}
            for param in params_list:
                valeurs[param] = st.text_input(f"{param}")
            bouton_perf = st.form_submit_button("Enregistrer la performance")
            if bouton_perf:
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute(
                    "INSERT INTO performances (exercice_id, date, donnees) VALUES (?, ?, ?)",
                    (ex_id, date, json.dumps(valeurs))
                )
                conn.commit()
                st.success(f"Performance enregistrée pour {choix} le {date}")

        # --- Historique des performances ---
        st.markdown("<h2 id='historique-des-performances'>Historique des performances</h2>", unsafe_allow_html=True)
        c.execute("SELECT date, donnees FROM performances WHERE exercice_id=? ORDER BY date DESC", (ex_id,))
        lignes = c.fetchall()
        if lignes:
            histo = []
            for date, donnees in lignes:
                data = json.loads(donnees)
                data["Date"] = date
                histo.append(data)
            st.dataframe(histo, use_container_width=True)
        else:
            st.info("Aucune performance enregistrée pour cet exercice.")
    else:
        st.info("Aucun exercice créé pour le moment.")

    conn.close()
