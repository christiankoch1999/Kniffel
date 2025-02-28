# app.py (angepasst für Render)
from flask import Flask, request, jsonify, render_template
import psycopg2
import os

app = Flask(__name__)

# Verbindungsdetails aus Environment Variables lesen
HOST = os.getenv("DB_HOST", "db.ocxoaevdhhwynzkkauhc.supabase.co")
PORT = os.getenv("DB_PORT", "5432")
DATABASE = os.getenv("DB_NAME", "postgres")
USER = os.getenv("DB_USER", "postgres")
PASSWORD = os.getenv("DB_PASSWORD", "Assc080265!")  # 🔴 Sollte als Environment Variable gesetzt werden!

# Datenbankverbindung herstellen
def get_db_connection():
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        dbname=DATABASE,
        user=USER,
        password=PASSWORD
    )
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_game', methods=['POST'])
def save_game():
    try:
        data = request.json
        print(f"Empfangene Daten: {data}")

        punktzahl_nina = data.get('punktzahl_nina')
        punktzahl_ck = data.get('punktzahl_ck')
        sieger = data.get('sieger')

        if punktzahl_nina is None or punktzahl_ck is None or sieger is None:
            return jsonify({"message": "Fehlende Daten", "status": "error"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # Tabelle erstellen, falls sie nicht existiert
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Games (
                id SERIAL PRIMARY KEY,
                punktzahl_nina BIGINT,
                punktzahl_ck BIGINT,
                sieger TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)

        cursor.execute(
            "INSERT INTO Games (punktzahl_nina, punktzahl_ck, sieger) VALUES (%s, %s, %s)",
            (punktzahl_nina, punktzahl_ck, sieger)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Spiel erfolgreich gespeichert!", "status": "success"}), 201

    except Exception as e:
        return jsonify({"message": "Fehler beim Speichern des Spiels", "status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv("PORT", 10000)))  # 🚀 Standard-Port von Render