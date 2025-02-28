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


# Datenbankverbindung herstellen
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=HOST,
            port=PORT,
            dbname=DATABASE,
            user=USER,
            password=PASSWORD
        )
        print("✅ Datenbankverbindung erfolgreich!")
        return conn
    except Exception as e:
        print(f"❌ Fehler bei der Datenbankverbindung: {e}")
        return None  # Falls die Verbindung fehlschlägt, gibt die Funktion None zurück

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
        if conn is None:
            return jsonify({"message": "Fehler: Keine Verbindung zur Datenbank", "status": "error"}), 500

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

        print("✅ Spiel erfolgreich gespeichert!")
        return jsonify({"message": "Spiel erfolgreich gespeichert!", "status": "success"}), 201

    except Exception as e:
        print(f"❌ Fehler beim Speichern: {e}")
        return jsonify({"message": "Fehler beim Speichern des Spiels", "status": "error", "error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv("PORT", 10000)))  # 🚀 Standard-Port von Render