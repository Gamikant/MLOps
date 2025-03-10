from airflow.models import BaseOperator
import requests
import logging
from bs4 import BeautifulSoup

class ScrapeGoogleNewsOperator(BaseOperator):
    def execute(self, context):
        ti = context["ti"]
        homepage_url = ti.xcom_pull(task_ids="get_homepage_url", key="homepage_url")
        if not homepage_url:
            logging.error("Homepage URL not found in XCom")
            raise ValueError("Homepage URL not found in XCom")

        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(homepage_url, headers=headers)
        if response.status_code != 200:
            logging.error(f"Failed to fetch Google News homepage: {response.status_code}")
            raise ValueError("Failed to fetch Google News homepage")

        soup = BeautifulSoup(response.content, "html.parser")
        logging.info("Successfully scraped Google News homepage")
        ti.xcom_push(key="html_code", value=str(soup))