from airflow import DAG
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python_operator import PythonOperator
from send_email_operator import SendEmailOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import os
import logging
import json

STATUS_FILE = "/opt/airflow/dags/run/status"
CONFIG_PATH = "/opt/airflow/config/config.json"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 2, 9),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def check_new_articles(**kwargs):
    """Reads the status file to get the number of new articles added."""
    if not os.path.exists(STATUS_FILE):
        logging.info("Status file not found, no new articles detected.")
        return []
    
    with open(STATUS_FILE, "r") as f:
        new_articles_count = int(f.read().strip())
    
    if new_articles_count <= 0:
        logging.info("No new articles found. Skipping email notification.")
        return []
    
    pg_hook = PostgresHook(postgres_conn_id="postgres_default")
    records = pg_hook.get_records("""
        SELECT title, link FROM news_metadata
        ORDER BY scrape_timestamp DESC LIMIT %s;
    """, parameters=(new_articles_count,))
    
    logging.info(f"Found {new_articles_count} new articles.")
    return records

def delete_status_file():
    """Deletes the status file after processing."""
    if os.path.exists(STATUS_FILE):
        os.remove(STATUS_FILE)
        logging.info("Deleted status file.")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as file:
            config = json.load(file)
        return config.get("recipient_email", "your_email@example.com")
    except Exception as e:
        logging.error(f"Failed to load email configuration: {e}")
        return "your_email@example.com"

with DAG(
    dag_id="send_email_dag",
    default_args=default_args,
    schedule_interval=None,  # Triggered by FileSensor
    catchup=False,
) as dag:

    wait_for_status_file = FileSensor(
        task_id="wait_for_status_file",
        filepath=STATUS_FILE,
        fs_conn_id="fs_default",
        poke_interval=10,
        mode = 'poke',
        timeout=600,
    )

    check_articles = PythonOperator(
        task_id="check_new_articles",
        python_callable=check_new_articles,
        provide_context=True,
    )

    send_email = SendEmailOperator(
        task_id="send_email",
        recipient=load_config(),
        subject="New Articles Alert",
    )

    cleanup_status = PythonOperator(
        task_id="delete_status_file",
        python_callable=delete_status_file,
    )

    wait_for_status_file >> check_articles >> send_email >> cleanup_status
