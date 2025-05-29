import streamlit as st
from datetime import datetime
import pandas as pd
from streamlit_gsheets import GSheetsConnection

def run():
    st.title("Mes Notes")

    # Connexion à Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Lecture des notes existantes
    df_notes = conn.read(worksheet="notes")
    if df_notes is None or df_notes.empty:
        df_notes = pd.DataFrame(columns=["date", "contenu"])

    # Formulaire pour ajouter une note
    with st.form("formulaire_note"):
        note = st.text_area("Écris ta note ici")
        bouton = st.form_submit_button("Enregistrer la note")

        if bouton and note.strip():
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Relire les notes existantes (sécurité)
            df_notes = conn.read(worksheet="notes", usecols=["date", "contenu"])
            if df_notes is None or df_notes.empty:
                df_notes = pd.DataFrame(columns=["date", "contenu"])
            # Ajouter la nouvelle note
            nouvelle_note = {"date": date_str, "contenu": note.strip()}
            df_notes = pd.concat([df_notes, pd.DataFrame([nouvelle_note])], ignore_index=True)
            # Réécrire tout dans la feuille
            conn.update(worksheet="notes", data=df_notes)
            st.success("Note enregistrée avec succès !")
            st.rerun()

    # Affichage des notes avec bouton de suppression
    st.subheader("Historique des notes")


    # DEBUG : afficher le DataFrame lu
    # st.write(df_notes)

    # Affichage du plus récent au plus ancien
    if not df_notes.empty:
        df_notes_sorted = df_notes.sort_values("date", ascending=False).reset_index(drop=True)
        for idx, row in df_notes_sorted.iterrows():
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"**{row['date']}**")
                st.write(row['contenu'])
            with col2:
                if st.button("Supprimer", key=f"suppr_{idx}"):
                    # Supprimer la note sélectionnée
                    df_notes_sorted = df_notes_sorted.drop(idx).reset_index(drop=True)
                    conn.update(worksheet="notes", data=df_notes_sorted)
                    st.success("Note supprimée avec succès !")
                    st.rerun()
            st.markdown("---")
    else:
        st.info("Aucune note enregistrée pour le moment.")
