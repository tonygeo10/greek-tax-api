import os
import psycopg2
import feedparser
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


SOURCES = [
    {
        "name": "Taxheaven",
        "url": "https://www.taxheaven.gr/bibliothiki/soft/xml/soft_new.xml",
        "category": "news"
    },
    {
        "name": "Taxheaven",
        "url": "https://www.taxheaven.gr/bibliothiki/soft/xml/soft_law.xml",
        "category": "law"
    },
    {
        "name": "Taxheaven",
        "url": "https://www.taxheaven.gr/bibliothiki/soft/xml/soft_art.xml",
        "category": "articles"
    },
    {
        "name": "Naftemporiki",
        "url": "https://www.naftemporiki.gr/finance/feed/",
        "category": "finance"
    }
]


def get_connection():
    return psycopg2.connect(DATABASE_URL)


def insert_article(cursor, title, link, category, source, published):
    cursor.execute("""
        INSERT INTO news_articles (title, link, category, source, published_at)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (link) DO NOTHING
    """, (title, link, category, source, published))


def scrape():
    conn = get_connection()
    cursor = conn.cursor()

    total_added = 0

    for source in SOURCES:
        print(f"🔎 Scraping {source['name']} - {source['category']}")

        feed = feedparser.parse(source["url"])

        for entry in feed.entries:
            title = entry.get("title")
            link = entry.get("link")

            published = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6])

            try:
                insert_article(
                    cursor,
                    title,
                    link,
                    source["category"],
                    source["name"],
                    published
                )
                total_added += 1
            except Exception as e:
                print("Insert error:", e)
                conn.rollback()

        conn.commit()

    conn.close()
    print(f"✅ Finished. Added: {total_added}")


if __name__ == "__main__":
    scrape()
