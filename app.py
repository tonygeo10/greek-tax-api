import os
import psycopg2
from flask import Flask, jsonify
from flask_cors import CORS # Εισαγωγή του CORS

app = Flask(__name__)
CORS(app) # Αυτό επιτρέπει στο GitHub Pages να "διαβάζει" το API σου

def get_db_connection():
    # Εδώ χρησιμοποιούμε το INTERNAL URL στο Render
    db_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(db_url)
    return conn

@app.route('/')
def index():
    return "Greek Tax API is running!"

@app.route('/api/news', methods=['GET'])
def get_news():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        # Βεβαιώσου ότι τα ονόματα των στηλών είναι ίδια με του scraper
        cur.execute("SELECT title, link, extracted_at FROM news_articles ORDER BY extracted_at DESC LIMIT 20")
        rows = cur.fetchall()
        
        articles = []
        for row in rows:
            articles.append({
                'title': row[0],
                'link': row[1],
                'extracted_at': row[2].isoformat() if row[2] else None
            })
        
        cur.close()
        conn.close()
        return jsonify(articles) # Επιστρέφει απευθείας τη λίστα
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
