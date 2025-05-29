import streamlit as st
import pandas as pd
from datetime import datetime
import json
from streamlit_gsheets import GSheetsConnection



def run():
    st.title("Suivi Gym")

    conn = st.connection("gsheets", type=GSheetsConnection)
    #st.write("Lecture de la table exercices à", datetime.now().strftime("%H:%M:%S"))

    if st.button("🔄 Rafraîchir les données"):
        st.cache_data.clear()
        st.rerun()

    # --- Ajouter un exercice ---
    with st.form(key="add_exercise_form"):
        nom_ex = st.text_input("Nom de l'exercice (ex : Elliptique, Développé couché, etc.)")
        parametres = st.text_area("Paramètres à suivre (séparés par des virgules, ex : km, durée, calories)")
        bouton_ex = st.form_submit_button("Ajouter l'exercice")
        if bouton_ex and nom_ex and parametres:
            # Lire toutes les données existantes
            df_exercices = conn.read(worksheet="exercices")
            if df_exercices is None or df_exercices.empty or "id" not in df_exercices.columns:
                df_exercices = pd.DataFrame(columns=["id", "nom", "parametres"])
            else:
                df_exercices["id"] = pd.to_numeric(df_exercices["id"], errors="coerce").astype("Int64")
            # Générer un nouvel ID
            new_id = int(df_exercices["id"].max() + 1) if not df_exercices.empty else 1
            nouvelle_ligne = {
                "id": new_id,
                "nom": nom_ex,
                "parametres": parametres
            }
            # Ajouter la nouvelle ligne
            df_exercices = pd.concat([df_exercices, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
            conn.update(worksheet="exercices", data=df_exercices)
            st.success(f"Exercice '{nom_ex}' ajouté avec les paramètres : {parametres}")
            st.cache_data.clear()
            st.rerun()

    # *** Relire le DataFrame exercices après ajout ***
    df_exercices = conn.read(worksheet="exercices")
    if df_exercices is None or df_exercices.empty:
        df_exercices = pd.DataFrame(columns=["id", "nom", "parametres"])
    else:
        # Nettoie les noms de colonnes
        df_exercices.columns = [c.strip().lower() for c in df_exercices.columns]
        if "id" not in df_exercices.columns:
            st.error(f"Colonne 'id' non trouvée ! Colonnes lues : {df_exercices.columns.tolist()}")
            st.stop()
        df_exercices["id"] = pd.to_numeric(df_exercices["id"], errors="coerce").astype("Int64")

    # --- Supprimer un exercice ---
    if not df_exercices.empty:
        ex_supp_dict = {f"{row.nom} ({row.parametres})": row.id for _, row in df_exercices.iterrows()}
        ex_supp_choix = st.selectbox("Sélectionne un exercice à supprimer", list(ex_supp_dict.keys()))
        if st.button("Supprimer cet exercice"):
            ex_id_to_del = ex_supp_dict[ex_supp_choix]
            # Lire toutes les données existantes
            df_exercices = conn.read(worksheet="exercices")
            if df_exercices is None or df_exercices.empty:
                df_exercices = pd.DataFrame(columns=["id", "nom", "parametres"])
            else:
                df_exercices["id"] = pd.to_numeric(df_exercices["id"], errors="coerce").astype("Int64")
            df_exercices = df_exercices[df_exercices["id"] != ex_id_to_del].reset_index(drop=True)
            conn.update(worksheet="exercices", data=df_exercices)
            # Supprimer les performances associées
            df_performances = conn.read(worksheet="performances")
            if df_performances is not None and not df_performances.empty and "exercice_id" in df_performances.columns:
                df_performances["exercice_id"] = pd.to_numeric(df_performances["exercice_id"], errors="coerce").astype("Int64")
                df_performances = df_performances[df_performances["exercice_id"] != ex_id_to_del].reset_index(drop=True)
                conn.update(worksheet="performances", data=df_performances)
            st.success(f"Exercice '{ex_supp_choix}' et ses performances associées supprimés.")
            st.cache_data.clear()
            st.rerun()
    else:
        st.info("Aucun exercice créé pour le moment.")

    # --- Enregistrer une performance ---
    if not df_exercices.empty:
        ex_options = {f"{row.nom} ({row.parametres})": (row.id, row.parametres) for _, row in df_exercices.iterrows()}
        choix = st.selectbox("Choisis un exercice", list(ex_options.keys()))
        ex_id, params = ex_options[choix]
        params_list = [p.strip() for p in params.split(",")]

        with st.form(key="add_performance_form"):
            valeurs = {}
            for param in params_list:
                valeurs[param] = st.text_input(f"{param}")
            bouton_perf = st.form_submit_button("Enregistrer la performance")
            if bouton_perf:
                # Lire toutes les données existantes
                df_performances = conn.read(worksheet="performances")
                if df_performances is None or df_performances.empty:
                    df_performances = pd.DataFrame(columns=["id", "exercice_id", "date", "donnees"])
                else:
                    df_performances["id"] = pd.to_numeric(df_performances["id"], errors="coerce").astype("Int64")
                    df_performances["exercice_id"] = pd.to_numeric(df_performances["exercice_id"], errors="coerce").astype("Int64")
                date_perf = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_perf_id = int(df_performances["id"].max() + 1) if not df_performances.empty else 1
                nouvelle_perf = {
                    "id": new_perf_id,
                    "exercice_id": ex_id,
                    "date": date_perf,
                    "donnees": json.dumps(valeurs)
                }
                df_performances = pd.concat([df_performances, pd.DataFrame([nouvelle_perf])], ignore_index=True)
                conn.update(worksheet="performances", data=df_performances)
                st.success(f"Performance enregistrée pour {choix} le {date_perf}")
                st.cache_data.clear()
                st.rerun()

        # *** Relire le DataFrame performances après ajout ***
        df_performances = conn.read(worksheet="performances")
        if df_performances is None or df_performances.empty:
            df_performances = pd.DataFrame(columns=["id", "exercice_id", "date", "donnees"])
        else:
            df_performances["id"] = pd.to_numeric(df_performances["id"], errors="coerce").astype("Int64")
            df_performances["exercice_id"] = pd.to_numeric(df_performances["exercice_id"], errors="coerce").astype("Int64")

        # --- Historique des performances ---
        st.markdown("<h2 id='historique-des-performances'>Historique des performances</h2>", unsafe_allow_html=True)
        perf_ex = df_performances[df_performances["exercice_id"] == ex_id]
        if not perf_ex.empty:
            histo = []
            for _, row in perf_ex.iterrows():
                data = json.loads(row["donnees"])
                data["Date"] = row["date"]
                histo.append(data)
            st.dataframe(pd.DataFrame(histo), use_container_width=True)
        else:
            st.info("Aucune performance enregistrée pour cet exercice.")
    else:
        st.info("Aucun exercice créé pour le moment.")
