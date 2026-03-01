import os
import requests
import psycopg2
from bs4 import BeautifulSoup
from datetime import datetime

print("🚀 Scraper started")
print("DB URL exists:", bool(os.environ.get("DATABASE_URL")))
print("DB URL starts with:", os.environ.get("DATABASE_URL", "")[:30])


SITES = [
    {
        "name": "AADE News",
        "url": "https://www.aade.gr/news",
        "selector": ".views-row a"
    },
    {
        "name": "AADE Nomothesia",
        "url": "https://www.aade.gr/nomothesia",
        "selector": ".views-row a"
    }
]


def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")

    if not db_url:
        raise Exception("❌ DATABASE_URL not found")

    # Ensure SSL for external Render DB
    if "sslmode" not in db_url:
        db_url += "?sslmode=require"

    return psycopg2.connect(db_url)


def scrape_site(site):
    print(f"\n🔎 Scraping: {site['name']}")
    print("URL:", site["url"])

    try:
        response = requests.get(
            site["url"],
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )

        print("Status code:", response.status_code)

        soup = BeautifulSoup(response.text, "html.parser")
        elements = soup.select(site["selector"])

        print("Elements found:", len(elements))

        results = []

        for a in elements:
            title = a.get_text(strip=True)
            link = a.get("href")

            if not title:
                continue

            if link and not link.startswith("http"):
                link = "https://www.aade.gr" + link

            results.append((title, link, site["name"]))

        print("Valid articles extracted:", len(results))
        return results

    except Exception as e:
        print(f"❌ Error scraping {site['name']}:", str(e))
        return []


def save_to_db(articles):
    if not articles:
        print("⚠ No articles to insert.")
        return 0

    conn = get_db_connection()
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
            print("DB insert error:", e)

    conn.commit()
    cur.close()
    conn.close()

    print("💾 Inserted new articles:", inserted)
    return inserted


def main():
    all_articles = []

    for site in SITES:
        articles = scrape_site(site)
        all_articles.extend(articles)

    print("\n📊 Total extracted from all sites:", len(all_articles))

    inserted = save_to_db(all_articles)

    print("✅ Scraper finished")
    print("New records added:", inserted)


if __name__ == "__main__":
    main()
