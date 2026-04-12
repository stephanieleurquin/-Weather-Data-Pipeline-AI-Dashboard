import requests
import sqlite3
import time
import csv
import matplotlib.pyplot as plt
from datetime import datetime

# 🌍 Villes (latitude, longitude)
CITIES = {
    "Bruxelles": (50.85, 4.35),
    "Paris": (48.85, 2.35),
    "Berlin": (52.52, 13.40),
    "Liège": (50.64, 5.57),
    "Huy": (50.52, 5.24)
}


# ---------------- EXTRACT ----------------
def extract(city, lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        weather = data["current_weather"]

        return {
            "city": city,
            "temperature": weather["temperature"],
            "windspeed": weather["windspeed"],
            "weathercode": weather["weathercode"],
            "time": weather["time"]
        }

    except Exception as e:
        print(f"❌ Erreur API pour {city} :", e)
        return None

# ---------------- TRANSFORM ----------------
def transform(data):
    if data is None:
        return None

    data["temperature"] = round(data["temperature"], 2)
    data["windspeed"] = round(data["windspeed"], 2)
    return data

# ---------------- LOAD SQLITE ----------------
def load_sqlite(data):
    conn = sqlite3.connect("meteo.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS meteo (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city TEXT,
        temperature REAL,
        windspeed REAL,
        weathercode INTEGER,
        time TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    INSERT INTO meteo (city, temperature, windspeed, weathercode, time)
    VALUES (?, ?, ?, ?, ?)
    """, (
        data["city"],
        data["temperature"],
        data["windspeed"],
        data["weathercode"],
        data["time"]
    ))

    conn.commit()
    conn.close()

# ---------------- EXPORT CSV ----------------
def export_csv():
    conn = sqlite3.connect("meteo.db")
    cursor = conn.cursor()

    cursor.execute("SELECT city, temperature, windspeed, weathercode, date FROM meteo")
    rows = cursor.fetchall()

    with open("meteo.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["city", "temperature", "windspeed", "weathercode", "date"])
        writer.writerows(rows)

    conn.close()
    print("📁 Export CSV terminé")

# ---------------- GRAPH ----------------
def plot_data():
    conn = sqlite3.connect("meteo.db")
    cursor = conn.cursor()

    cursor.execute("SELECT date, temperature FROM meteo ORDER BY date")
    data = cursor.fetchall()

    conn.close()

    dates = [row[0] for row in data]
    temps = [row[1] for row in data]

    plt.figure()
    plt.plot(dates, temps)
    plt.xticks(rotation=45)
    plt.title("Température dans le temps")
    plt.xlabel("Date")
    plt.ylabel("Température")
    plt.tight_layout()
    plt.show()

# ---------------- PIPELINE ----------------
def run_pipeline():
    for city, coords in CITIES.items():
        lat, lon = coords

        raw = extract(city, lat, lon)
        clean = transform(raw)

        if clean:
            load_sqlite(clean)
            print(f"✔ Données enregistrées pour {city}")

# ---------------- MAIN LOOP ----------------
print("🚀 Lancement pipeline météo...")

for city, coords in CITIES.items():
    lat, lon = coords

    raw = extract(city, lat, lon)
    clean = transform(raw)

    if clean:
        load_sqlite(clean)
        print(f"✔ Données enregistrées pour {city}")

export_csv()
plot_data()

print("✅ Terminé")
