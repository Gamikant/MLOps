from airflow import DAG
from airflow.decorators import task
from get_homepage_url_operator import GetHomepageURLOperator
from scrape_google_news_operator import ScrapeGoogleNewsOperator
from extract_top_stories_link_operator import ExtractTopStoriesLinkOperator
from get_thumbnail_caption_operator import GetThumbnailCaptionOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from store_data_postgres_operator import StoreArticlesToPostgresOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime, timedelta
import logging
import json
import os
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logging.info("Modules imported successfully inside the DAG file")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}

with DAG(
    dag_id="pipeline",
    default_args=default_args,
    schedule="@hourly",
    start_date=datetime(2025, 2, 9),
    catchup=False,
) as dag:

    get_homepage_link = GetHomepageURLOperator(task_id="get_homepage_url")
    scrape_google_news_page = ScrapeGoogleNewsOperator(task_id="scrape_google_news")
    extract_top_stories = ExtractTopStoriesLinkOperator(task_id="extract_top_stories_link")
    thumbnail_caption = GetThumbnailCaptionOperator(task_id="get_thumbnail_caption")
    create_tables = PostgresOperator(task_id="create_tables",postgres_conn_id="postgres_default",
        sql="""
            CREATE TABLE IF NOT EXISTS news_images (
                id SERIAL PRIMARY KEY,
                image_data BYTEA NOT NULL
            );

            CREATE TABLE IF NOT EXISTS news_metadata (
                id SERIAL PRIMARY KEY,
                title TEXT UNIQUE,
                link TEXT,
                date DATE,
                time TIME,
                image_id INTEGER REFERENCES news_images(id),
                scrape_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """,
    )
    store_articles = StoreArticlesToPostgresOperator(task_id="store_articles_in_postgres",postgres_conn_id="postgres_default")
    trigger_send_email = TriggerDagRunOperator(task_id="trigger_send_email_dag",trigger_dag_id="send_email_dag", wait_for_completion=False)


    get_homepage_link  >> scrape_google_news_page >> extract_top_stories >> thumbnail_caption >> create_tables>> store_articles >> trigger_send_email
