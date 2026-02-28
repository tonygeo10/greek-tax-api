import os
import psycopg2
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@app.route('/')
def home():
    return "API is running!"

@app.route('/api/news')
def get_news():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT title, link, extracted_at FROM news_articles ORDER BY extracted_at DESC LIMIT 20")
    rows = cur.fetchall()
    articles = [{"title": r[0], "link": r[1], "date": r[2].isoformat()} for r in rows]
    cur.close()
    conn.close()
    return jsonify({"articles": articles})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
