import streamlit as st
import pandas as pd
from datetime import date
from streamlit_gsheets import GSheetsConnection

OBJECTIF_CAL = 1800

def run():
    st.title("Suivi nutritionnel")

    conn = st.connection("gsheets", type=GSheetsConnection)
    
    if st.button("🔄 Rafraîchir les données"):
        st.cache_data.clear()
        st.rerun()

    selected_date = st.date_input("Date", value=date.today())
    st.markdown(f"**Objectif calorique : {OBJECTIF_CAL} kcal**")

    # Formulaire d'ajout d'aliment
    with st.form(key="add_food_form"):
        food = st.text_input("Aliment")
        calories = st.number_input("Calories", min_value=0, step=1)
        submitted = st.form_submit_button("Ajouter")
        if submitted and food and calories:
            nouvelle_ligne = {
                "entry_date": str(selected_date),
                "food": food,
                "calories": int(calories)
            }
            # Lire toutes les données existantes
            df_nutrition = conn.read(worksheet="nutrition")
            if df_nutrition is None or df_nutrition.empty:
                df_nutrition = pd.DataFrame(columns=["entry_date", "food", "calories"])
            # Ajouter la nouvelle ligne à toutes les données
            df_nutrition = pd.concat([df_nutrition, pd.DataFrame([nouvelle_ligne])], ignore_index=True)
            conn.update(worksheet="nutrition", data=df_nutrition)
            st.success(f"{food} ajouté ({calories} kcal)")
            st.cache_data.clear()
            st.rerun()

    # *** C'est ICI qu'on relit le DataFrame ***
    df_nutrition = conn.read(worksheet="nutrition")
    if df_nutrition is None or df_nutrition.empty:
        df_nutrition = pd.DataFrame(columns=["entry_date", "food", "calories"])

    # Filtrage par date
    foods = df_nutrition[df_nutrition["entry_date"] == str(selected_date)]
    total_cal = foods["calories"].astype(int).sum() if not foods.empty else 0

    if not foods.empty:
        for idx, row in foods.iterrows():
            col1, col2, col3 = st.columns([5, 2, 1])
            with col1:
                st.write(row["food"])
            with col2:
                st.write(f"{row['calories']} kcal")
            with col3:
                if st.button("🗑️", key=f"del_{idx}"):
                    mask = (
                        (df_nutrition["entry_date"] == row["entry_date"]) &
                        (df_nutrition["food"] == row["food"]) &
                        (df_nutrition["calories"] == row["calories"])
                    )
                    df_nutrition = df_nutrition[~mask].reset_index(drop=True)
                    conn.update(worksheet="nutrition", data=df_nutrition)
                    st.success("Aliment supprimé !")
                    st.cache_data.clear()
                    st.rerun()
    else:
        st.write("Aucun aliment enregistré pour cette date.")

    st.markdown("---")
    st.markdown(f"### Total : **{total_cal} kcal**")
    if total_cal > OBJECTIF_CAL:
        st.error("🚨 Objectif dépassé !")
    elif total_cal == OBJECTIF_CAL:
        st.success("🎯 Objectif atteint !")
    else:
        st.info(f"Il te reste {OBJECTIF_CAL - total_cal} kcal avant d'atteindre l'objectif.")
