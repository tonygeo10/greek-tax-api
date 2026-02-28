import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv

load_dotenv()

AADE_URL = "https://www.aade.gr/egkyklioi-kai-apofaseis"

def run_scraper():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(AADE_URL, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        articles = []

        # 👉 Βρίσκουμε ΜΟΝΟ links που ανήκουν σε ανακοινώσεις
        for link in soup.select("a[href*='/egkyklioi-kai-apofaseis/']"):
            title = link.get_text(strip=True)
            href = link.get("href")

            if not title:
                continue

            if len(title) < 15:
                continue

            if not href.startswith("http"):
                href = f"https://www.aade.gr{href}"

            articles.append((title, href))

        print(f"Found {len(articles)} valid AADE articles")

        # --- DATABASE ---
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

        inserted = 0

        for title, link in articles:
            cur.execute("""
                INSERT INTO news_articles (title, link)
                VALUES (%s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (title, link))

            if cur.rowcount > 0:
                inserted += 1

        conn.commit()
        cur.close()
        conn.close()

        print(f"Inserted {inserted} new articles")

    except Exception as e:
        print("ERROR:", e)


if __name__ == "__main__":
    run_scraper()
