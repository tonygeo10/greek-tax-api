import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def run_scraper():
    url = "https://www.aade.gr/egkyklioi-kai-apofaseis"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        articles = []

        # ΣΩΣΤΟΣ SELECTOR για ΑΑΔΕ
        for item in soup.select("div.views-row"):
            link_tag = item.select_one("a")
            if link_tag:
                title = link_tag.get_text(strip=True)
                href = link_tag["href"]

                if title and href:
                    full_link = href if href.startswith("http") else f"https://www.aade.gr{href}"
                    articles.append((title, full_link))

        print(f"Found {len(articles)} articles from AADE")

        # DATABASE
        db_url = os.environ.get("DATABASE_URL")
        conn = psycopg2.connect(db_url, sslmode="require")
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        for title, link in articles:
            cur.execute("""
                INSERT INTO news_articles (title, link)
                VALUES (%s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (title, link))

        conn.commit()

        cur.close()
        conn.close()

        print(f"Success! Inserted {len(articles)} articles.")

    except Exception as e:
        print("ERROR:", e)

if __name__ == "__main__":
    run_scraper()
