import streamlit as st
import sqlite3
from datetime import date

OBJECTIF_CAL = 1800

def get_connection():
    conn = sqlite3.connect("data.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nutrition (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL,
            food TEXT NOT NULL,
            calories INTEGER NOT NULL
        )
    """)
    conn.commit()
    return conn

def add_food(conn, food, calories, entry_date):
    conn.execute(
        "INSERT INTO nutrition (entry_date, food, calories) VALUES (?, ?, ?)",
        (entry_date, food, calories)
    )
    conn.commit()

def get_foods(conn, entry_date):
    cur = conn.execute(
        "SELECT id, food, calories FROM nutrition WHERE entry_date = ?",
        (entry_date,)
    )
    return cur.fetchall()

def delete_food(conn, food_id):
    conn.execute("DELETE FROM nutrition WHERE id = ?", (food_id,))
    conn.commit()

def run():
    st.title("Suivi nutritionnel")
    conn = get_connection()

    selected_date = st.date_input("Date", value=date.today())
    st.markdown(f"**Objectif calorique : {OBJECTIF_CAL} kcal**")

    # Formulaire d'ajout d'aliment
    with st.form(key="add_food_form"):
        food = st.text_input("Aliment")
        calories = st.number_input("Calories", min_value=0, step=1)
        submitted = st.form_submit_button("Ajouter")
        if submitted and food and calories:
            add_food(conn, food, int(calories), str(selected_date))
            st.success(f"{food} ajouté ({calories} kcal)")
            st.experimental_rerun()

    # Affichage des aliments consommés ce jour
    st.subheader(f"Aliments consommés le {selected_date.strftime('%d/%m/%Y')}")
    foods = get_foods(conn, str(selected_date))
    total_cal = sum([c for _, _, c in foods])

    if foods:
        for food_id, food_name, cal in foods:
            col1, col2, col3 = st.columns([5, 2, 1])
            with col1:
                st.write(food_name)
            with col2:
                st.write(f"{cal} kcal")
            with col3:
                if st.button("🗑️", key=f"del_{food_id}"):
                    delete_food(conn, food_id)
                    st.experimental_rerun()
    else:
        st.write("Aucun aliment enregistré pour cette date.")

    # Affichage du total et indication visuelle
    st.markdown("---")
    st.markdown(f"### Total : **{total_cal} kcal**")
    if total_cal > OBJECTIF_CAL:
        st.error("🚨 Objectif dépassé !")
    elif total_cal == OBJECTIF_CAL:
        st.success("🎯 Objectif atteint !")
    else:
        st.info(f"Il te reste {OBJECTIF_CAL - total_cal} kcal avant d'atteindre l'objectif.")

    conn.close()
