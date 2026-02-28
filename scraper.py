import requests
from bs4 import BeautifulSoup
import psycopg2

def run_scraper():
    # Use the specific 'Circulars' page which is highly active
    url = "https://www.aade.gr/egkyklioi-kai-apofaseis" 
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    
    print(f"Connecting to: {url}...")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 404:
            print("Error 404: The URL is incorrect. Trying fallback URL...")
            # Fallback to the homepage if the specific section fails
            url = "https://www.aade.gr/"
            response = requests.get(url, headers=headers, timeout=10)

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        # AADE's current layout uses 'views-field-title' and 'views-field-nothing'
        # We also look for links containing 'pdf' or 'egkyklioi'
        for link_tag in soup.find_all('a', href=True):
            title = link_tag.get_text(strip=True)
            href = link_tag['href']
            
            # Filter for actual news/decisions (usually longer titles)
            if len(title) > 30 and ('/egkyklioi' in href or 'deltia-typoy' in href):
                full_link = href if href.startswith('http') else f"https://www.aade.gr{href}"
                articles.append((title, full_link))

        if not articles:
            print("Connected, but found 0 headlines. The structure might be protected.")
            return

        # DATABASE CONNECTION
        conn = psycopg2.connect(
            host="localhost",
            database="tax_hub",
            user="postgres",
            password="123456" # <--- Update this!
        )
        cur = conn.cursor()

        for title, link in articles:
            cur.execute(
                "INSERT INTO news_articles (title, link) VALUES (%s, %s) ON CONFLICT (link) DO NOTHING",
                (title, link)
            )

        conn.commit()
        print(f"Success! Found {len(articles)} items.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            cur.close()
            conn.close()

if __name__ == "__main__":
    run_scraper()