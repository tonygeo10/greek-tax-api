def scrape_site(site):
    print(f"\n🔎 Scraping: {site['name']}")
    print("URL:", site["url"])

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "el-GR,el;q=0.9,en;q=0.8",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(
            site["url"],
            headers=headers,
            timeout=20
        )

        print("Status code:", response.status_code)

        if response.status_code != 200:
            print("❌ Blocked by server")
            return []
