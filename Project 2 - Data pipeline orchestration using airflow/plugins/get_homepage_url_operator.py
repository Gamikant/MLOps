from airflow.models import BaseOperator
import json
import logging

class GetHomepageURLOperator(BaseOperator):
    def __init__(self, config_path="/opt/airflow/config/config.json", **kwargs):
        super().__init__(**kwargs)
        self.config_path = config_path
    
    def execute(self, context):
        try:
            with open(self.config_path, "r") as file:
                homepage_url = json.load(file).get("homepage_url", "https://news.google.com")
            logging.info(f"Homepage URL fetched: {homepage_url}")
            context["ti"].xcom_push(key="homepage_url", value=homepage_url)
        except FileNotFoundError:
            logging.error(f"Config file not found: {self.config_path}")
            raise