from airflow.models import BaseOperator
import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

class GetThumbnailCaptionOperator(BaseOperator):
    def execute(self, context):
        ti = context["ti"]
        top_stories_link = ti.xcom_pull(task_ids="extract_top_stories_link", key="top_stories_link")
        if not top_stories_link:
            logging.warning("Top stories link is empty")
            ti.xcom_push(key="thumbnail_captions_list", value=[])
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(top_stories_link, headers=headers)
        if response.status_code != 200:
            logging.error("Failed to fetch top stories page")
            ti.xcom_push(key="thumbnail_captions_list", value=[])
        soup = BeautifulSoup(response.content, "html.parser")
        logging.info("Top stories page scraped")
        articles = soup.find_all("article")
        results = []
        for article in articles:
            a_tag = article.find("a", class_="gPFEn")
            title = a_tag.get_text(strip=True) if a_tag else None
            link = "https://news.google.com" + a_tag["href"][1:] if a_tag and "href" in a_tag.attrs else None
            figure = article.find("figure")
            img_tag = figure.find("img") if figure else None
            img_src = img_tag["src"] if img_tag else None
            if img_src and img_src.startswith("/"):
                img_src = "https://news.google.com" + img_src
            date_time_div = article.find("div", class_="UOVeFe")
            time_tag = date_time_div.find("time") if date_time_div else None
            datetime_str = time_tag["datetime"] if time_tag else None
            if datetime_str:
                dt_obj = datetime.strptime(datetime_str, "%Y-%m-%dT%H:%M:%SZ")
                ist_time = dt_obj + timedelta(hours=5, minutes=30)
                date = ist_time.date().isoformat()
                time = ist_time.time().isoformat()
            else:
                date, time = None, None
            if img_src:
                results.append({"title": title, "link": link, "thumbnail": img_src, "date": date, "time": time})
        ti.xcom_push(key="thumbnail_captions_list", value=results)