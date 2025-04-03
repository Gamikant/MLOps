import json
import requests
from bs4 import BeautifulSoup

def load_config():
    with open("config.json", "r") as file:
        return json.load(file)

def scrape_google_news():
    config = load_config()
    homepage_url = config.get("homepage_url", "https://news.google.com")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(homepage_url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch Google News homepage")
        return None
    soup = BeautifulSoup(response.content, "html.parser")
    return soup