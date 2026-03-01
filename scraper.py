import os
import requests
import psycopg2
from bs4 import BeautifulSoup

print("🚀 Scraper started")

DATABASE_URL = os.environ.get("DATABASE_URL")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
    "Referer": "https://www.google.com/"
}


SOURCES = [
    {
        "name": "AADE Announcements",
        "url": "https://www.aade.gr/anakoinoseis"
    },
    {
        "name": "AADE Nomothesia",
        "url": "https://www.aade.gr/nomothesia"
    }
]


def scrape_site(source):
    print(f"\n🔎 Scraping: {source['name']}")
    print("URL:", source["url"])

    try:
        response = requests.get(source["url"], headers=HEADERS, timeout=15)
        print("Status code:", response.status_code)

        if response.status_code != 200:
            print("❌ Request blocked or failed")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        items = soup.find_all("div", class_="views-field-title")
        print("Elements found:", len(items))

        results = []

        for item in items:
            link_tag = item.find("a")
            if link_tag:
                title = link_tag.get_text(strip=True)
                link = link_tag.get("href")

                if not link.startswith("http"):
                    link = "https://www.aade.gr" + link

                results.append((title, link, source["name"]))

        print("Valid articles extracted:", len(results))
        return results

    except Exception as e:
        print("❌ Exception:", e)
        return []


def save_to_db(articles):
    if not articles:
        print("⚠ No articles to insert")
        return 0

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    inserted = 0

    for title, link, source in articles:
        try:
            cur.execute("""
                INSERT INTO news_articles (title, link, source)
                VALUES (%s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (title, link, source))
            inserted += 1
        except Exception as e:
            print("Insert error:", e)

    conn.commit()
    cur.close()
    conn.close()

    return inserted


# MAIN
all_articles = []

for source in SOURCES:
    articles = scrape_site(source)
    all_articles.extend(articles)

print("\n📊 Total extracted:", len(all_articles))

new_records = save_to_db(all_articles)

print("✅ Scraper finished")
print("New records added:", new_records)
