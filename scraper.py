import requests
from bs4 import BeautifulSoup

def scrape_latest_20():
    url = "https://www.aade.gr/news"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    articles = soup.select("h3 a")[:20]  # adjust selector if needed

    for a in articles:
        title = a.get_text(strip=True)
        link = a["href"]
        if not link.startswith("http"):
            link = "https://www.aade.gr" + link
        results.append((title, link))

    return results
