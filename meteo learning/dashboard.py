import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

st.set_page_config(page_title="🌤️ Météo IA", layout="centered")

st.title("🌤️ Dashboard Météo + IA")

# ---------------- LOAD DATA ----------------
import os
db_path = os.path.join(os.path.dirname(__file__), "meteo.db")
conn = sqlite3.connect(db_path)
df = pd.read_sql_query("SELECT * FROM meteo", conn)
conn.close()

# ❌ si pas de données
if df.empty:
    st.error("❌ Aucune donnée. Lance apimeteo.py d'abord.")
    st.stop()

# ---------------- FILTRE VILLE ----------------
if "city" in df.columns:
    city = st.selectbox("🌍 Choisir une ville", df["city"].unique())
    df = df[df["city"] == city]

# ---------------- TIME ----------------
df["time"] = range(len(df))

# ---------------- SHOW DATA ----------------
st.subheader("📁 Données météo")
st.dataframe(df)

# ---------------- GRAPH ----------------
st.subheader("📊 Température dans le temps")

df["time"] = range(len(df))

fig, ax = plt.subplots()
ax.plot(df["time"], df["temperature"], marker="o")

ax.set_xlabel("Temps")
ax.set_ylabel("Température (°C)")
ax.set_title("Évolution de la température")

st.pyplot(fig)

# ---------------- MACHINE LEARNING ----------------
st.subheader("🧠 Prédiction IA")

X = df[["time"]]
y = df["temperature"]

model = LinearRegression()
model.fit(X, y)

future = pd.DataFrame([[len(df) + 1]], columns=["time"])
prediction = model.predict(future)

st.success(f"🔮 Température prévue : {round(prediction[0], 2)} °C")

# ---------------- REFRESH ----------------
if st.button("🔄 Rafraîchir"):
    st.rerun()
