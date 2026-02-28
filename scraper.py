import requests
from bs4 import BeautifulSoup

def scrape_tax_news():
    url = "https://www.aade.gr/news"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    results = []

    # Βρες όλα τα links που περιέχουν /news/
    for link in soup.find_all("a", href=True):
        href = link["href"]

        if "/news/" in href:
            title = link.get_text(strip=True)

            if len(title) > 10:
                full_link = href if href.startswith("http") else f"https://www.aade.gr{href}"
                results.append((title, full_link))

    # Αφαίρεση duplicates
    results = list(set(results))

    return results


if __name__ == "__main__":
    articles = scrape_tax_news()
    print(f"Found {len(articles)} articles")
    for a in articles[:10]:
        print(a)
