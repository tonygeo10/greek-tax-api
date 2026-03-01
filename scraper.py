import os
import requests
import psycopg2
from bs4 import BeautifulSoup
db_url = os.environ.get("DATABASE_URL")
print("DB URL starts with:", db_url.split("@")[0] if db_url else "None")
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

def scrape_latest_20():
    url = "https://www.aade.gr/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []
    articles = soup.select("h3 a")[:20]

    for a in articles:
        title = a.get_text(strip=True)
        link = a["href"]

        if not link.startswith("http"):
            link = "https://www.aade.gr" + link

        results.append((title, link, "AADE"))

    return results


def save_to_db(articles):
    conn = get_connection()
    cur = conn.cursor()

    for title, link, source in articles:
        try:
            cur.execute("""
                INSERT INTO news_articles (title, link, source)
                VALUES (%s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (title, link, source))
        except Exception as e:
            print("Insert error:", e)

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    articles = scrape_latest_20()
    save_to_db(articles)
    print(f"Success! Captured {len(articles)} articles.")
