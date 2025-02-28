from flask import Flask, request, jsonify, render_template
import psycopg2

app = Flask(__name__)

# Verbindungsdetails (ersetze sie mit deinen eigenen)
HOST = 'db.ocxoaevdhhwynzkkauhc.supabase.co'
PORT = '5432'
DATABASE = 'postgres'
USER = 'postgres'
PASSWORD = 'Assc080265!'

# Versuche, eine Verbindung mit PostgreSQL herzustellen
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
        # Daten aus der POST-Anfrage entnehmen
        data = request.json
        print(f"Empfangene Daten: {data}")  # Protokolliere die empfangenen Daten

        punktzahl_nina = data.get('punktzahl_nina')
        punktzahl_ck = data.get('punktzahl_ck')
        sieger = data.get('sieger')

        # Überprüfen, ob alle Felder vorhanden sind
        if punktzahl_nina is None or punktzahl_ck is None or sieger is None:
            print(f"Fehlende Daten: punktzahl_nina: {punktzahl_nina}, punktzahl_ck: {punktzahl_ck}, sieger: {sieger}")
            return jsonify({"message": "Fehlende Daten", "status": "error"}), 400

        # Stelle die Verbindung zur Datenbank her
        conn = get_db_connection()
        cursor = conn.cursor()

        # Tabelle Games überprüfen und erstellen, falls sie nicht existiert
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Games (
                id SERIAL PRIMARY KEY,
                punktzahl_nina BIGINT,
                punktzahl_ck BIGINT,
                sieger TEXT,
                created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Füge das Spiel in die Supabase-Datenbank ein
        cursor.execute(
            "INSERT INTO Games (punktzahl_nina, punktzahl_ck, sieger) VALUES (%s, %s, %s)",
            (punktzahl_nina, punktzahl_ck, sieger)
        )

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Spiel erfolgreich gespeichert!", "status": "success"}), 201

    except Exception as e:
        print(f"Fehler beim Speichern des Spiels: {e}")
        return jsonify({"message": "Fehler beim Speichern des Spiels", "status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
