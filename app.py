import os
import psycopg2
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# -----------------------
# Database Connection
# -----------------------
def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")

    if not db_url:
        raise Exception("DATABASE_URL environment variable not set")

    conn = psycopg2.connect(db_url, sslmode="require")
    return conn


# -----------------------
# Routes
# -----------------------
@app.route("/")
def index():
    return "Greek Tax API is running!"


@app.route("/api/news", methods=["GET"])
def get_news():
    conn = None
    cur = None

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT title, link, extracted_at
            FROM news_articles
            ORDER BY extracted_at DESC
            LIMIT 20
        """)

        rows = cur.fetchall()

        articles = [
            {
                "title": row[0],
                "link": row[1],
                "date": row[2].isoformat() if row[2] else None
            }
            for row in rows
        ]

        return jsonify(articles)

    except Exception as e:
        print("ERROR:", e)  # Θα το βλέπεις στα Render logs
        return jsonify({"error": str(e)}), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# -----------------------
# Run (Render compatible)
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
