from flask import Flask, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
# IMPORTANT: This allows your GitHub Pages site to talk to this server
CORS(app) 

def get_db_connection():
    # Render will automatically provide this 'DATABASE_URL'
    return psycopg2.connect(os.environ.get('DATABASE_URL'))

@app.route('/api/news')
def get_news():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT title, link, extracted_at FROM news_articles ORDER BY extracted_at DESC LIMIT 20")
        rows = cur.fetchall()
        
        # Convert the SQL data into a list for the website
        articles = [{"title": r[0], "link": r[1], "date": str(r[2])} for r in rows]
        
        cur.close()
        conn.close()
        return jsonify(articles)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run()