import sqlite3


conn = sqlite3.connect("meteo.db")
cursor = conn.cursor ()

cursor.execute("""
CREATE TABLE IF NOT EXISTS meteo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ville TEXT,
    temperature REAL,
    vent REAL,
    pluie REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()






