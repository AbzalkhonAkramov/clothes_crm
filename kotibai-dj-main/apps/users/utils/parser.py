import requests
from bs4 import BeautifulSoup


def scrape_site(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        page_content = response.text

        soup = BeautifulSoup(page_content, 'html.parser')

        h1_tags = soup.find_all('h1')
        p_tags = soup.find_all('p')

        content = []

        for h1 in h1_tags:
            content.append(h1.get_text())

        for p in p_tags:
            content.append(p.get_text())

        return "\n\n".join(content)

    except requests.exceptions.RequestException as e:
        print(f"Xatolik yuz berdi: {e}")
        return None
