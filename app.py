import os
import psycopg2
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Allow GitHub Pages frontend
CORS(app, resources={
    r"/api/*": {
        "origins": "https://tonygeo10.github.io"
    }
})

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    return psycopg2.connect(db_url)

@app.route("/")
def index():
    return "Greek Tax API is running!"

@app.route("/api/news", methods=["GET"])
def get_news():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT title, link, source, created_at
            FROM news_articles
            ORDER BY created_at DESC
            LIMIT 20
        """)

        rows = cur.fetchall()

        articles = [
            {
                "title": row[0],
                "link": row[1],
                "source": row[2],
                "created_at": row[3].isoformat() if row[3] else None
            }
            for row in rows
        ]

        cur.close()
        conn.close()

        return jsonify(articles)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
