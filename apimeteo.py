import streamlit as st
import sqlite3
import requests
from datetime import datetime
import pandas as pd

st.title("🌤️ Météo Live PRO")

cities = {
    "Paris": (48.8566, 2.3522),
    "Bruxelles": (50.85, 4.35),
    "Liège": (50.6333, 5.5667),
    "Namur": (50.4669, 4.8675),
    "Huy": (50.5192, 5.2328),
    "Amay": (50.5500, 5.3167)
}

city = st.selectbox("🌍 Choisir une ville", list(cities.keys()))
lat, lon = cities[city]

# 🌦️ API CORRECTE (current + daily)
def get_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    return requests.get(url).json()

data = get_weather()

# ======================
# 🌡️ CURRENT WEATHER
# ======================
current = data["current_weather"]


st.metric("🌡️ Température", f"{current['temperature']} °C")
st.metric("💨 Vent", f"{current['windspeed']} km/h")

st.write("🕒 Heure API :", current["time"].replace("T", " "))
st.write("🕒 Heure locale :", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ======================
# 📅 DAILY (7 jours)
# ======================
df = pd.DataFrame({
    "date": data["daily"]["time"],
    "temp_max": data["daily"]["temperature_2m_max"],
    "temp_min": data["daily"]["temperature_2m_min"],
    "pluie": data["daily"]["precipitation_sum"]
})
conn = sqlite3.connect("meteo.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO meteo (ville, temperature, vent, pluie, date)
VALUES (?, ?, ?, ?, ?)
""", (
    city,
    current["temperature"],
    current["windspeed"],
    df["pluie"].iloc[0],
    current["time"]
))

conn.commit()
conn.close()

st.subheader("📅 Prévisions 7 jours")
st.dataframe(df)

st.line_chart(df.set_index("date")[["temp_max", "temp_min"]])

# ======================
# 🌧️ PLUIE
# ======================
st.subheader("🌧️ Pluie aujourd'hui")
st.write(f"{df['pluie'].iloc[0]} mm")

# ======================
# 🗺️ CARTE
# ======================
st.subheader("🗺️ Carte")
st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}))
