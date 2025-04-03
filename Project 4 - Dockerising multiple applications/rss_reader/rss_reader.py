import os
import time
import logging
import feedparser
import requests
import psycopg2
from datetime import datetime
from urllib.parse import urlparse
import hashlib
import pathlib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("rss_reader")

# Get environment variables with defaults
RSS_URL = os.getenv('RSS_URL', 'https://www.thehindu.com/news/national/?service=rss')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', 600))  # 10 minutes in seconds
DB_HOST = os.getenv('DB_HOST', 'db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'rssfeeds')
DB_USER = os.getenv('POSTGRES_USER', 'rssuser')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'rsspassword')

# RSS feed field mappings (configurable via env vars)
TITLE_PATH = os.getenv('TITLE_PATH', 'title')
TIMESTAMP_PATH = os.getenv('TIMESTAMP_PATH', 'published')
LINK_PATH = os.getenv('LINK_PATH', 'link')
IMAGE_PATH = os.getenv('IMAGE_PATH', 'media_content')
TAGS_PATH = os.getenv('TAGS_PATH', 'tags')
SUMMARY_PATH = os.getenv('SUMMARY_PATH', 'summary')

# Directory to store images
IMAGE_DIR = pathlib.Path('/app/images')
IMAGE_DIR.mkdir(exist_ok=True)

def get_db_connection():
    """Establish a connection to the database"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

def download_image(url):
    """Download image from URL and save to disk"""
    if not url:
        return None
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            # Create a filename based on URL hash
            filename = hashlib.md5(url.encode()).hexdigest() + os.path.splitext(urlparse(url).path)[1]
            filepath = IMAGE_DIR / filename
            
            # Save the image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            return str(filepath)
        else:
            logger.warning(f"Failed to download image: {url}, status code: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error downloading image {url}: {e}")
        return None

def parse_timestamp(timestamp_str):
    """Parse timestamp string to datetime object"""
    try:
        # Handle common RSS date formats
        formats = [
            '%a, %d %b %Y %H:%M:%S %z',  # RFC 822 format
            '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601 format
            '%Y-%m-%d %H:%M:%S',         # Simple format
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue
        
        # If all formats fail, use feedparser's parser
        time_struct = feedparser._parse_date(timestamp_str)
        if time_struct:
            return datetime(*time_struct[:6])
        
        raise ValueError(f"Could not parse timestamp: {timestamp_str}")
    except Exception as e:
        logger.error(f"Error parsing timestamp {timestamp_str}: {e}")
        return datetime.now()  # Fallback to current time

def get_nested_value(data, path):
    """Get a value from a nested dictionary using a dot-separated path"""
    if not path:
        return None
    
    parts = path.split('.')
    result = data
    
    for part in parts:
        if isinstance(result, dict) and part in result:
            result = result[part]
        elif isinstance(result, list) and part.isdigit() and int(part) < len(result):
            result = result[int(part)]
        else:
            return None
    
    return result

def process_entry(entry):
    """Process a single RSS feed entry"""
    # Extract required fields
    title = get_nested_value(entry, TITLE_PATH)
    if not title:
        logger.warning(f"Skipping entry without title: {entry}")
        return None
    
    weblink = get_nested_value(entry, LINK_PATH)
    if not weblink:
        logger.warning(f"Skipping entry without weblink: {entry}")
        return None
    
    # Get timestamp and parse it
    timestamp_str = get_nested_value(entry, TIMESTAMP_PATH)
    publication_timestamp = parse_timestamp(timestamp_str) if timestamp_str else datetime.now()
    
    # Extract image URL and download it
    image_url = None
    media_content = get_nested_value(entry, IMAGE_PATH)
    if media_content:
        if isinstance(media_content, list) and len(media_content) > 0:
            image_url = media_content[0].get('url')
        elif isinstance(media_content, dict):
            image_url = media_content.get('url')
    
    image_path = download_image(image_url) if image_url else None
    
    # Extract tags
    tags = []
    entry_tags = get_nested_value(entry, TAGS_PATH)
    if entry_tags and isinstance(entry_tags, list):
        for tag in entry_tags:
            if isinstance(tag, dict) and 'term' in tag:
                tags.append(tag['term'])
    
    # Extract summary
    summary = get_nested_value(entry, SUMMARY_PATH)
    if summary and isinstance(summary, dict) and 'value' in summary:
        summary = summary['value']
    
    return (title, publication_timestamp, weblink, image_path, tags, summary)

def save_to_database(conn, article_data):
    """Save article data to database"""
    try:
        with conn.cursor() as cur:
            # Check if article with same link already exists
            cur.execute(
                "SELECT id FROM news_articles WHERE weblink = %s",
                (article_data[2],)
            )
            if cur.fetchone():
                logger.info(f"Article already exists: {article_data[0]}")
                return False
            
            # Insert new article
            cur.execute(
                """
                INSERT INTO news_articles 
                (title, publication_timestamp, weblink, image_path, tags, summary)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    article_data[0],                  # title
                    article_data[1],                  # publication_timestamp
                    article_data[2],                  # weblink
                    article_data[3],                  # image_path
                    article_data[4] if article_data[4] else [],  # tags
                    article_data[5]                   # summary
                )
            )
            conn.commit()
            logger.info(f"Saved article: {article_data[0]}")
            return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving article to database: {e}")
        return False

def fetch_and_process_feed():
    """Fetch RSS feed and process entries"""
    try:
        logger.info(f"Fetching RSS feed from: {RSS_URL}")
        feed = feedparser.parse(RSS_URL)
        
        if not feed.entries:
            logger.warning("No entries found in the RSS feed")
            return 0
        
        logger.info(f"Found {len(feed.entries)} entries in the feed")
        
        # Connect to database
        conn = get_db_connection()
        
        saved_count = 0
        for entry in feed.entries:
            article_data = process_entry(entry)
            if article_data:
                if save_to_database(conn, article_data):
                    saved_count += 1
        
        conn.close()
        logger.info(f"Saved {saved_count} new articles to the database")
        return saved_count
    
    except Exception as e:
        logger.error(f"Error processing RSS feed: {e}")
        return 0

def main():
    """Main function to run the RSS reader"""
    logger.info("Starting RSS reader application")
    
    while True:
        try:
            fetch_and_process_feed()
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
        
        logger.info(f"Sleeping for {POLL_INTERVAL} seconds")
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    main()
