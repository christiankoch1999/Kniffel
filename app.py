from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import psycopg2

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


# Verbindungsdetails aus Environment Variables lesen
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_NAME")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")


import psycopg2
import os

def get_db_connection():
    try:
        print("🛠 Versuche, eine Verbindung zur Datenbank herzustellen...")
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode="disable"  # IPv6-Probleme umgehen
        )
        print("✅ Verbindung zur Datenbank erfolgreich!")
        return conn
    except Exception as e:
        print(f"❌ Fehler bei der Datenbankverbindung: {e}")  # Log an Render senden
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_game', methods=['POST'])
def save_game():
    try:
        data = request.json
        print(f"📥 Empfangene Daten: {data}")

        conn = get_db_connection()
        if conn is None:
            return jsonify({"message": "Fehler: Keine Verbindung zur Datenbank", "status": "error"}), 500

        cursor = conn.cursor()

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
            (data.get('punktzahl_nina'), data.get('punktzahl_ck'), data.get('sieger'))
        )

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Spiel erfolgreich gespeichert!")
        return jsonify({"message": "Spiel erfolgreich gespeichert!", "status": "success"}), 201

    except Exception as e:
        print(f"❌ Fehler beim Speichern des Spiels: {e}")
        return jsonify({"message": "Fehler beim Speichern", "status": "error", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv("PORT", 10000)))  # 🚀 Standard-Port von Render