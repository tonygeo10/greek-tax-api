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

        for link_tag in soup.find_all('a', href=True):
            title = link_tag.get_text(strip=True)
            if len(title) > 25:
                href = link_tag['href']
                full_link = href if href.startswith('http') else f"https://www.aade.gr{href}"
                articles.append((title, full_link))

        # 2. DATABASE CONNECTION
        db_url = os.environ.get('DATABASE_URL')
        
        # Προσθέτουμε sslmode='require' για τη σύνδεση από το GitHub Actions στο Render
        conn = psycopg2.connect(db_url, sslmode='require')
        cur = conn.cursor()

        # ΑΥΤΟ ΗΤΑΝ ΤΟ ΚΛΕΙΔΙ: Δημιουργία του πίνακα αν δεν υπάρχει
        cur.execute('''
            CREATE TABLE IF NOT EXISTS news_articles (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                link TEXT UNIQUE NOT NULL,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

        # 3. INSERT DATA
        for title, link in articles:
            cur.execute(
                "INSERT INTO news_articles (title, link) VALUES (%s, %s) ON CONFLICT (link) DO NOTHING",
                (title, link)
            )

        conn.commit()
        print(f"Success! Captured {len(articles)} articles and ensured table exists.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    run_scraper()
