 import os
import requests
import psycopg2
from bs4 import BeautifulSoup
from datetime import datetime

print("🚀 Scraper started")

DB_URL = os.environ.get("DATABASE_URL")

print("DB URL exists:", bool(DB_URL))

if not DB_URL:
    raise Exception("DATABASE_URL not set")


def get_connection():
    return psycopg2.connect(DB_URL, sslmode="require")


def scrape_aade_news():
    print("\n🔎 Scraping AADE News")

    url = "https://www.aade.gr/news"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "el-GR,el;q=0.9"
    }

    response = requests.get(url, headers=headers, timeout=20)

    print("Status code:", response.status_code)

    if response.status_code != 200:
        print("❌ Request failed")
        return []

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("div.views-row")

    print("HTML elements found:", len(rows))

    results = []

    for row in rows:
        a = row.find("a")
        if not a:
            continue

        title = a.get_text(strip=True)
        link = a.get("href")

        if not link:
            continue

        if not link.startswith("http"):
            link = "https://www.aade.gr" + link

        results.append((title, link, "AADE News"))

    print("Valid extracted:", len(results))

    return results


def insert_articles(articles):

    if not articles:
        print("⚠ No articles to insert")
        return

    conn = get_connection()
    cur = conn.cursor()

    inserted = 0

    for title, link, source in articles:
        cur.execute("""
            INSERT INTO news_articles (title, link, source, created_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (link) DO NOTHING
        """, (title, link, source, datetime.utcnow()))

        if cur.rowcount > 0:
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()

    print("🆕 New records inserted:", inserted)


# ---------------- MAIN ----------------

articles = scrape_aade_news()

print("\n📊 Total extracted:", len(articles))

insert_articles(articles)

print("✅ Scraper finished")
