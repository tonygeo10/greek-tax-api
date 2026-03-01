import os
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg2.connect(DATABASE_URL)


@app.route("/api/articles")
def get_articles():
    category = request.args.get("category")
    page = int(request.args.get("page", 1))
    per_page = 10
    offset = (page - 1) * per_page

    conn = get_connection()
    cursor = conn.cursor()

    if category:
        cursor.execute("""
            SELECT COUNT(*) FROM news_articles WHERE category = %s
        """, (category,))
    else:
        cursor.execute("SELECT COUNT(*) FROM news_articles")

    total = cursor.fetchone()[0]
    total_pages = (total + per_page - 1) // per_page

    if category:
        cursor.execute("""
            SELECT title, link, category, source, published_at
            FROM news_articles
            WHERE category = %s
            ORDER BY published_at DESC
            LIMIT %s OFFSET %s
        """, (category, per_page, offset))
    else:
        cursor.execute("""
            SELECT title, link, category, source, published_at
            FROM news_articles
            ORDER BY published_at DESC
            LIMIT %s OFFSET %s
        """, (per_page, offset))

    rows = cursor.fetchall()

    articles = [
        {
            "title": row[0],
            "link": row[1],
            "category": row[2],
            "source": row[3],
            "published_at": row[4].isoformat() if row[4] else None
        }
        for row in rows
    ]

    conn.close()

    return jsonify({
        "articles": articles,
        "page": page,
        "total_pages": total_pages
    })

@app.route("/")
def home():
    return "Greek Tax News API running 🚀"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
