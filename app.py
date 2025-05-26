import streamlit as st

st.set_page_config(page_title="Suivi Forme", page_icon="🏋️")

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Aller à :",
    ("Accueil", "Poids", "Gym", "Notes", "Suivi nutritionnel", "Télécharger les bases")
)

if page == "Télécharger les bases":
    import telechargement_db
    telechargement_db.run()

elif page == "Accueil":
    st.title("Bienvenue Alexandre !")
    st.write("Bienvenue Alexandre sur ton app de suivi nutritionnelle et sportive !")

elif page == "Poids":
    import poids
    poids.run()

elif page == "Gym":
    import gym
    gym.run()

elif page == "Notes":
    import notes
    notes.run()

elif page == "Suivi nutritionnel":
    import nutrition
    nutrition.run()
