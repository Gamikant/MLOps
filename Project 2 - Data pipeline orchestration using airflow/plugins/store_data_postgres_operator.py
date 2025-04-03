from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import base64
import os
import requests

class StoreArticlesToPostgresOperator(BaseOperator):
    def __init__(self, postgres_conn_id="postgres_default", **kwargs):
        super().__init__(**kwargs)
        self.postgres_conn_id = postgres_conn_id

    def execute(self, context):
        ti = context["ti"]
        articles = ti.xcom_pull(task_ids="get_thumbnail_caption", key="thumbnail_captions_list")
        
        if not articles:
            self.log.warning("No articles found to store.")
            return

        pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        inserted_count = 0  

        for article in articles:
            title, link, date, time, img_url = (
                article["title"],
                article["link"],
                article["date"],
                article["time"],
                article["thumbnail"],
            )

            cursor.execute("SELECT id FROM news_metadata WHERE title = %s;", (title,))
            existing_article = cursor.fetchone()

            if existing_article:
                self.log.info(f"Skipping duplicate article: {title}")
                continue 

            try:
                image_response = requests.get(img_url)
                if image_response.status_code == 200:
                    img_base64 = base64.b64encode(image_response.content).decode("utf-8")
                else:
                    img_base64 = None
            except:
                img_base64 = None

            if img_base64:
                cursor.execute("INSERT INTO news_images (image_data) VALUES (%s) RETURNING id;", (img_base64,))
                image_id = cursor.fetchone()[0]
            else:
                image_id = None

            cursor.execute(
                """
                INSERT INTO news_metadata (title, link, date, time, image_id)
                VALUES (%s, %s, %s, %s, %s);
                """,
                (title, link, date, time, image_id)
            )

            inserted_count += 1

        conn.commit()
        cursor.close()
        conn.close()

        status_file_path = "/opt/airflow/dags/run/status"
        os.makedirs(os.path.dirname(status_file_path), exist_ok=True)
        with open(status_file_path, "w") as f:
            f.write(str(inserted_count))

        self.log.info(f"Stored {inserted_count} new articles in PostgreSQL.")