from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import psycopg2

app = Flask(__name__)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')




def get_db_connection():
    try:
        print("🛠 Verbinde mit Supabase über den Session Pooler...")
        conn = psycopg2.connect(
    dbname="postgres",
    user="postgres.ocxoaevdhhwynzkkauhc",
    password="Assc080265!",
    host="aws-0-eu-central-1.pooler.supabase.com",
    port="6543",
    sslmode="require"
)

        
        print("✅ Verbindung erfolgreich!")
        return conn
    except Exception as e:
        print(f"❌ Fehler bei der Verbindung: {e}")
        return None  # Falls Fehler auftreten, gibt die Funktion None zurück


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

@app.route('/stats', methods=["GET"])
def stats():
    try:
        conn = get_db_connection()

        if conn is None:
            return jsonify({"message": "Fehler: Keine Verbindung zur Datenbank", "status": "error"}), 500

        cursor = conn.cursor()

        # Siege von Nina abrufen
        cursor.execute("SELECT COUNT(*) FROM Games WHERE sieger = 'Nina';")
        siege_nina = cursor.fetchone()[0]  # Nur die Zahl extrahieren

        # Siege von Ck abrufen
        cursor.execute("SELECT COUNT(*) FROM Games WHERE sieger = 'Ck';")
        siege_ck = cursor.fetchone()[0]

        cursor.close()
        conn.close()

        # Ergebnisse zurückgeben
        return jsonify({
            "siege_nina": siege_nina,
            "siege_ck": siege_ck,
            "status": "success"
        }), 200

    except Exception as e:
        print(f"❌ Fehler in /stats: {e}")
        return jsonify({"message": "Fehler beim Abrufen der Statistiken", "status": "error"}), 500



if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv("PORT", 10000)))  # 🚀 Standard-Port von Render