from airflow.models import BaseOperator
import logging
from bs4 import BeautifulSoup

class ExtractTopStoriesLinkOperator(BaseOperator):
    def execute(self, context):
        ti = context["ti"]
        html_code = ti.xcom_pull(task_ids="scrape_google_news", key="html_code")
        soup = BeautifulSoup(html_code, "html.parser")
        if not soup:
            logging.error("HTML code couldn't be parsed")
            raise ValueError("HTML code couldn't be parsed")
        top_stories_section = soup.select_one("div.n3GXRc")
        if top_stories_section:
            a_tag = top_stories_section.select_one("h3 a")
            if a_tag and "href" in a_tag.attrs:
                logging.info("Top stories link extracted")
                ti.xcom_push(key="top_stories_link", value="https://news.google.com" + a_tag["href"][1:])
        logging.warning("Top stories section not found")