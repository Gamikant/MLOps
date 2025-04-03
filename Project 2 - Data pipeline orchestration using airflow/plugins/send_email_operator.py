from airflow.models import BaseOperator
import smtplib
import logging
import json
from email.mime.text import MIMEText

CONFIG_PATH = "/opt/airflow/config/config.json"

class SendEmailOperator(BaseOperator):
    def __init__(self, recipient, subject, **kwargs):
        super().__init__(**kwargs)
        self.recipient = recipient
        self.subject = subject
    
    def execute(self, context):
        ti = context["ti"]
        new_articles = ti.xcom_pull(task_ids="check_new_articles")
        
        if not new_articles or len(new_articles) == 0:
            logging.info("No new articles to email. Skipping email notification.")
            return
        
        try:
            with open(CONFIG_PATH, "r") as file:
                config = json.load(file)
            SMTP_SERVER = config.get("smtp_server", "smtp.gmail.com")
            SMTP_PORT = config.get("smtp_port", 587)
            SMTP_USERNAME = config.get("smtp_username")
            SMTP_PASSWORD = config.get("smtp_password")
            if not SMTP_USERNAME or not SMTP_PASSWORD:
                raise ValueError("SMTP credentials are missing in config.json")
        except Exception as e:
            logging.error(f"Failed to load SMTP configuration: {e}")
            raise
        
        email_body = "New Articles inserted:\n\n"
        for title, link in new_articles:
            email_body += f"{title} - {link}\n"
        
        msg = MIMEText(email_body)
        msg["Subject"] = self.subject
        msg["From"] = SMTP_USERNAME
        msg["To"] = self.recipient
        
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(SMTP_USERNAME, [self.recipient], msg.as_string())
            server.quit()
            logging.info("Email sent successfully.")
        except smtplib.SMTPAuthenticationError as e:
            logging.error("SMTP Authentication Error: Check if your username/password are correct, enable 'Less Secure Apps' or use an App Password if 2FA is enabled.")
            raise
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            raise
