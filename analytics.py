import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_gsheets import GSheetsConnection

def run():
    st.title("Analytics")

    # Connexion à Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Lecture du poids
    df_poids = conn.read(worksheet="poids")
    df_poids.columns = [c.strip().lower() for c in df_poids.columns]
    df_poids = df_poids.rename(columns={"date": "date", "valeur": "poids"})
    df_poids["date"] = pd.to_datetime(df_poids["date"], errors="coerce").dt.date
    df_poids["poids"] = pd.to_numeric(df_poids["poids"], errors="coerce")
    df_poids = df_poids.groupby("date", as_index=False).mean()

    # Lecture de la nutrition
    df_nutrition = conn.read(worksheet="nutrition")
    df_nutrition.columns = [c.strip().lower() for c in df_nutrition.columns]
    df_nutrition = df_nutrition.rename(columns={"entry_date": "date"})
    df_nutrition["date"] = pd.to_datetime(df_nutrition["date"], errors="coerce").dt.date
    df_nutrition["calories"] = pd.to_numeric(df_nutrition["calories"], errors="coerce").fillna(0)
    calories_par_jour = df_nutrition.groupby("date", as_index=False)["calories"].sum().sort_values("date")

    # Fusion OUTER pour garder toutes les dates de poids
    df_merged = pd.merge(df_poids, calories_par_jour, on="date", how="left")
    df_merged["calories"] = df_merged["calories"].fillna(0)

    # Décaler les calories d'un jour vers le bas pour aligner calories veille <-> poids du jour
    df_merged = df_merged.sort_values("date")
    df_merged["calories_veille"] = df_merged["calories"].shift(1, fill_value=0)

    if df_merged.empty:
        st.warning("Aucune donnée à afficher.")
        st.stop()

    # Création du graphique combiné
    fig = go.Figure()

    # Courbe du poids
    fig.add_trace(go.Scatter(
        x=df_merged["date"], y=df_merged["poids"],
        mode="lines+markers", name="Poids (kg)", yaxis="y1",
        line=dict(color="black", width=3)
    ))

    # Barres pour les calories de la veille
    fig.add_trace(go.Bar(
        x=df_merged["date"], y=df_merged["calories_veille"],
        name="Calories mangées la veille", yaxis="y2", opacity=0.6
    ))

    # Mise en page avec deux axes Y
    fig.update_layout(
        title="Poids du jour vs calories mangées la veille",
        xaxis_title="Date",
        yaxis=dict(title="Poids (kg)", side="left"),
        yaxis2=dict(title="Calories mangées la veille", overlaying="y", side="right"),
        barmode="group",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Voir les données fusionnées"):
        st.dataframe(df_merged)
