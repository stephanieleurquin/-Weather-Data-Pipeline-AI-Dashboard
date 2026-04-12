import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression

# 📊 Charger les données
conn = sqlite3.connect("meteo.db")

df = pd.read_sql_query("SELECT temperature FROM meteo", conn)
conn.close()

# ❌ sécurité si pas de données
if len(df) < 2:
    print("❌ Pas assez de données. Lance apimeteo.py plusieurs fois.")
    exit()

# ⏱️ créer un temps artificiel
df["time"] = range(len(df))

X = df[["time"]]
y = df["temperature"]

# 🧠 modèle ML
model = LinearRegression()
model.fit(X, y)

# 🔮 prédiction future
future_time = [[len(df) + 1]]
prediction = model.predict(future_time)

print("📊 Données utilisées :", len(df))
print("🔮 Température prévue :", round(prediction[0], 2))