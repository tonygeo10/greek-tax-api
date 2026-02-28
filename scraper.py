import os
import requests
from bs4 import BeautifulSoup
import psycopg2
from dotenv import load_dotenv

# 1. Load variables from .env (only used for local development)
load_dotenv()

def run_scraper():
    url = "https://www.aade.gr/egkyklioi-kai-apofaseis"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        # (Your existing scraping logic to find headlines)
        for link_tag in soup.find_all('a', href=True):
            title = link_tag.get_text(strip=True)
            if len(title) > 25:
                href = link_tag['href']
                full_link = href if href.startswith('http') else f"https://www.aade.gr{href}"
                articles.append((title, full_link))

        # 2. DATABASE CONNECTION
        # This will get the URL from .env (local) or Render Dashboard (cloud)
        db_url = os.environ.get('DATABASE_URL')
        
        # Connect to Render (sslmode is required for external connections)
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        for title, link in articles:
            cur.execute(
                "INSERT INTO news_articles (title, link) VALUES (%s, %s) ON CONFLICT (link) DO NOTHING",
                (title, link)
            )

        conn.commit()
        print(f"Success! Captured {len(articles)} articles to the cloud.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    run_scraper()