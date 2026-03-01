import os
import requests
import psycopg2
from bs4 import BeautifulSoup
from datetime import datetime
import feedparser

print("🚀 Scraper started")

DB_URL = os.environ.get("DATABASE_URL")
print("DB URL exists:", bool(DB_URL))

if not DB_URL:
    raise Exception("DATABASE_URL not set")

print("DB URL starts with:", DB_URL[:35])


# -------------------------
# DB CONNECTION
# -------------------------
def get_connection():
    return psycopg2.connect(DB_URL, sslmode="require")


# -------------------------
# GENERIC HTML SCRAPER
# -------------------------
def scrape_html(name, url):
    print(f"\n🔎 Scraping HTML: {name}")
    print("URL:", url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
        "Accept-Language": "el-GR,el;q=0.9"
    }

    try:
        r = requests.get(url, headers=headers, timeout=20)
        print("Status code:", r.status_code)

        if r.status_code != 200:
            print("⚠ Blocked or failed")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select("div.views-row")

        print("HTML elements found:", len(rows))

        results = []

        for row in rows:
            a = row.select_one("a")
            if a:
                title = a.get_text(strip=True)
                link = a.get("href")

                if not link:
                    continue

                if not link.startswith("http"):
                    link = "https://www.aade.gr" + link

                results.append((title, link, name))

        print("Valid extracted:", len(results))
        return results

    except Exception as e:
        print("❌ HTML scrape error:", e)
        return []


# -------------------------
# RSS SCRAPER
# -------------------------
def scrape_rss(name, url):
    print(f"\n📡 Trying RSS: {name}")
    print("URL:", url)

    try:
        feed = feedparser.parse(url)
        print("Entries found:", len(feed.entries))

        results = []

        for entry in feed.entries:
            results.append((entry.title, entry.link, name))

        print("Valid RSS extracted:", len(results))
        return results

    except Exception as e:
        print("❌ RSS error:", e)
        return []


# -------------------------
# INSERT INTO DATABASE
# -------------------------
def insert_articles(articles):
    if not articles:
        print("⚠ No articles to insert.")
        return 0

    conn = get_connection()
    cur = conn.cursor()

    inserted = 0

    for title, link, source in articles:
        try:
            cur.execute("""
                INSERT INTO news_articles (title, link, source, created_at)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (title, link, source, datetime.utcnow()))
            
            if cur.rowcount > 0:
                inserted += 1

        except Exception as e:
            print("Insert error:", e)

    conn.commit()
    cur.close()
    conn.close()

    print("🆕 New records inserted:", inserted)
    return inserted


# -------------------------
# MAIN EXECUTION
# -------------------------

all_articles = []

# 1️⃣ Try RSS first (most stable)
all_articles += scrape_rss("AADE RSS", "https://www.aade.gr/rss.xml")

# 2️⃣ Fallback HTML
all_articles += scrape_html("AADE News", "https://www.aade.gr/news")
all_articles += scrape_html("AADE Nomothesia", "https://www.aade.gr/nomothesia")

print("\n📊 Total extracted:", len(all_articles))

insert_articles(all_articles)

print("✅ Scraper finished")
    return results

        if response.status_code != 200:
            print("❌ Blocked by server")
            return []
