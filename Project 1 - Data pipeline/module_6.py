import logging
import time
from module_1 import scrape_google_news
from module_2 import extract_top_stories_link
from module_3 import get_thumbnail_caption
from module_4 import store_data

logging.basicConfig(filename="orchestrator.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def run_pipeline():
    logging.info("Pipeline started")
    start_time = time.time()
    try:
        scrape_google_news()
        logging.info("Module 1 executed successfully")
        extract_top_stories_link()
        logging.info("Module 2 executed successfully")
        get_thumbnail_caption()
        logging.info("Module 3 executed successfully")
        store_data()
        logging.info("Module 4 executed successfully using Module 5")
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
    finally:
        logging.info(f"Pipeline completed in {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    run_pipeline()