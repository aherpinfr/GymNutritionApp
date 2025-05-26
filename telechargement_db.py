import streamlit as st
import os

def run():
    st.title("Télécharger les bases de données")

    # Liste des fichiers de bases à proposer
    db_files = [
        ("Base principale (suivi_forme.db)", "suivi_forme.db"),
        ("Base poids (poids.db)", "poids.db"),
        ("Base nutrition (data.db)", "data.db")
    ]

    for label, filename in db_files:
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                st.download_button(
                    label=f"Télécharger {label}",
                    data=f,
                    file_name=filename,
                    mime="application/octet-stream"
                )
        else:
            st.warning(f"{label} non trouvée ({filename})")

    st.info("Télécharge régulièrement tes bases pour ne pas perdre tes données lors d’un redémarrage de l’application.")
