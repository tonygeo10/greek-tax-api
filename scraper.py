import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.aade.gr"

SECTIONS = [
    "/news",
    "/egkyklioi-kai-apofaseis",
    "/deltia-typou",
    "/anakoinoseis",
    "/enhmerotika-deltia",
    "/nomothesia"
]

headers = {
    "User-Agent": "Mozilla/5.0"
}

def scrape_all_aade_sections():
    results = []

    for section in SECTIONS:
        url = BASE_URL + section
        print(f"Scraping: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")

            # Βρίσκουμε όλα τα links που έχουν πραγματικό τίτλο
            for a in soup.find_all("a", href=True):
                title = a.get_text(strip=True)

                if len(title) > 30:  # φιλτράρισμα άχρηστων links
                    link = a["href"]
                    full_link = link if link.startswith("http") else BASE_URL + link

                    results.append({
                        "section": section,
                        "title": title,
                        "link": full_link
                    })

        except Exception as e:
            print(f"Error in {section}: {e}")

    return results


if __name__ == "__main__":
    articles = scrape_all_aade_sections()
    print(f"\nFound {len(articles)} articles\n")

    for art in articles[:10]:
        print(art["title"])
