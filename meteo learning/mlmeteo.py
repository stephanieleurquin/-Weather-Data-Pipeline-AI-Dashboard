import requests
import sqlite3
import pandas as pd
import time
from sklearn.linear_model import LinearRegression

# 🌍 Ville
CITY = "Bruxelles"
LAT, LON = 50.85, 4.35

# ------------------ 1. EXTRACTION ------------------
def get_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={LAT}&longitude={LON}&current_weather=true"
    response = requests.get(url)
    data = response.json()["current_weather"]

    return {
        "temperature": data["temperature"],
        "windspeed": data["windspeed"],
        "time": data["time"]
    }

# ------------------ 2. STOCKAGE ------------------
def save_to_db(data):
    conn = sqlite3.connect("meteo.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meteo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        temperature REAL,
        windspeed REAL,
        time TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    INSERT INTO meteo (temperature, windspeed, time)
    VALUES (?, ?, ?)
    """, (
        data["temperature"],
        data["windspeed"],
        data["time"]
    ))

    conn.commit()
    conn.close()

# ------------------ 3. MACHINE LEARNING ------------------
def predict_temperature():
    conn = sqlite3.connect("meteo.db")

    df = pd.read_sql_query("SELECT temperature, windspeed, date FROM meteo", conn)
    conn.close()

    if len(df) < 5:
        print("❌ Pas assez de données (min 5)")
        return

    # convertir date en timestamp
    df["date"] = pd.to_datetime(df["date"])
    df["time"] = df["date"].map(lambda x: x.timestamp())

    # variables
    X = df[["time", "windspeed"]]
    y = df["temperature"]

    # modèle
    model = LinearRegression()
    model.fit(X, y)

    # prédiction future
    future_time = time.time()
    future_wind = df["windspeed"].iloc[-1]

    prediction = model.predict([[future_time, future_wind]])

    # vérification
    last_real = df["temperature"].iloc[-1]
    error = abs(last_real - prediction[0])

    print(f"\n📊 Ville : {CITY}")
    print("🌡️ Dernière température :", last_real)
    print("🔮 Température prévue :", round(prediction[0], 2), "°C")
    print("📏 Erreur estimée :", round(error, 2), "°C")

# ------------------ MAIN ------------------
print("🚀 Récupération météo...")

data = get_weather()
save_to_db(data)

print("✔ Données enregistrées")

predict_temperature()
