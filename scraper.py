import os
import requests
import psycopg2
import xml.etree.ElementTree as ET
from datetime import datetime
print("DATABASE_URL:", os.environ.get("DATABASE_URL"))
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SOURCES = {
    "Taxheaven Feed": "https://www.taxheaven.gr/feed/",
    "Soft New": "https://www.taxheaven.gr/bibliothiki/soft/xml/soft_new.xml",
    "Soft Law": "https://www.taxheaven.gr/bibliothiki/soft/xml/soft_law.xml",
    "Soft Articles": "https://www.taxheaven.gr/bibliothiki/soft/xml/soft_art.xml",
}

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    return psycopg2.connect(db_url)

def scrape_xml(name, url):
    print(f"🔎 Scraping {name}")
    print(f"URL: {url}")

    response = requests.get(url, headers=HEADERS, timeout=15)
    print("Status:", response.status_code)

    if response.status_code != 200:
        print("❌ Failed")
        return []

    root = ET.fromstring(response.content)

    articles = []

    for item in root.findall(".//item"):
        title = item.findtext("title")
        link = item.findtext("link")

        if title and link:
            articles.append({
                "title": title.strip(),
                "link": link.strip(),
                "source": name
            })

    print(f"✅ Found {len(articles)} items")
    return articles

def insert_articles(articles):
    if not articles:
        print("⚠ No articles to insert")
        return 0

    conn = get_db_connection()
    cur = conn.cursor()

    inserted = 0

    for art in articles:
        try:
            cur.execute("""
                INSERT INTO news_articles (title, link, source)
                VALUES (%s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (art["title"], art["link"], art["source"]))
            inserted += cur.rowcount
        except Exception as e:
            print("Insert error:", e)

    conn.commit()
    cur.close()
    conn.close()

    return inserted

def run_scraper():
    print("🚀 Scraper started")

    all_articles = []

    for name, url in SOURCES.items():
        try:
            articles = scrape_xml(name, url)
            all_articles.extend(articles)
        except Exception as e:
            print("❌ Error:", e)

    print(f"📊 Total extracted: {len(all_articles)}")

    new_records = insert_articles(all_articles)

    print(f"🆕 New records added: {new_records}")
    print("✅ Scraper finished")

    return new_records


if __name__ == "__main__":
    run_scraper()
