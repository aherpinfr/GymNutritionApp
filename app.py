import streamlit as st

st.set_page_config(page_title="Suivi Forme", page_icon="🏋️")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à :", ("Accueil", "Poids", "Gym"))

if page == "Accueil":
    st.title("Bienvenue Alexandre !")
    st.write("Bienvenue Alexandre sur ton app de suivi nutritionnel et sportif !")
elif page == "Poids":
    import poids
    poids.run()
elif page == "Gym":
    import gym
    gym.run()