import streamlit as st
import sqlite3
from datetime import datetime

def run():
    conn = sqlite3.connect('suivi_forme.db')
    c = conn.cursor()

    # Création de la table notes si elle n'existe pas
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            contenu TEXT
        )
    ''')
    conn.commit()

    st.title("Mes Notes")

    # Formulaire pour ajouter une note
    with st.form("formulaire_note"):
        note = st.text_area("Écris ta note ici")
        bouton = st.form_submit_button("Enregistrer la note")

        if bouton and note.strip():
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO notes (date, contenu) VALUES (?, ?)", (date, note.strip()))
            conn.commit()
            st.success("Note enregistrée avec succès !")

    # Affichage des notes avec bouton de suppression
    st.subheader("Historique des notes")

    c.execute("SELECT id, date, contenu FROM notes ORDER BY date DESC")
    notes = c.fetchall()

    if notes:
        for note_id, date, contenu in notes:
            col1, col2 = st.columns([8, 1])
            with col1:
                st.markdown(f"**{date}**")
                st.write(contenu)
            with col2:
                if st.button("Supprimer", key=f"suppr_{note_id}"):
                    c.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                    conn.commit()
                    st.success("Note supprimée avec succès !")
                    st.experimental_rerun()
            st.markdown("---")
    else:
        st.info("Aucune note enregistrée pour le moment.")

    conn.close()
