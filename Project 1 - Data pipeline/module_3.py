import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from module_2 import extract_top_stories_link

def parse_datetime(datetime_str):
    dt_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
    ist_time = dt_obj + timedelta(hours=5, minutes=30)
    return ist_time.date().isoformat(), ist_time.time().isoformat()

def get_thumbnail_caption():
    top_stories_link = extract_top_stories_link()
    if not top_stories_link:
        return []
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(top_stories_link, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch top stories page")
        return []
    soup = BeautifulSoup(response.content, "html.parser")
    articles = soup.find_all("article")
    results = []
    for article in articles:
        a_tag = article.find("a", class_="gPFEn")
        title = a_tag.get_text(strip=True) if a_tag else "No title found"
        link = "https://news.google.com" + a_tag["href"][1:] if a_tag and "href" in a_tag.attrs else "No link found"
        figure = article.find("figure")
        img_tag = figure.find("img") if figure else None
        img_src = img_tag["src"] if img_tag else "No image found"
        if img_src.startswith("/"):
            img_src = "https://news.google.com" + img_src
        date_time_div = article.find("div", class_="UOVeFe")
        time_tag = date_time_div.find("time") if date_time_div else None
        datetime_str = time_tag["datetime"] if time_tag else "No date time found"
        date, time = parse_datetime(datetime_str) if datetime_str != "No date time found" else ("Unknown", "Unknown")
        results.append({"title": title, "link": link, "thumbnail": img_src, "date": date, "time": time})
    return results