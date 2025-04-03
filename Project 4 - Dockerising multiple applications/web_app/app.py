from flask import Flask, render_template, request, redirect
import psycopg2
import psycopg2.extras
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'db')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('POSTGRES_DB', 'rssfeeds')
DB_USER = os.getenv('POSTGRES_USER', 'rssuser')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'rsspassword')

def get_db_connection():
    """Establish a connection to the database"""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.cursor_factory = psycopg2.extras.DictCursor
    return conn


@app.route('/')
def index():
    # Get date filter from query parameters, default to today
    date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    try:
        # Parse the date
        filter_date = datetime.strptime(date_filter, '%Y-%m-%d')
        next_date = filter_date + timedelta(days=1)
        
        # Connect to the database
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query articles for the selected date
        cur.execute(
            """
            SELECT id, title, publication_timestamp, weblink, image_path, tags, summary
            FROM news_articles
            WHERE publication_timestamp >= %s AND publication_timestamp < %s
            ORDER BY publication_timestamp DESC
            """,
            (filter_date, next_date)
        )
        
        articles = cur.fetchall()
        cur.close()
        conn.close()
        
        return render_template(
            'index.html', 
            articles=articles, 
            date_filter=date_filter,
            today=datetime.now().strftime('%Y-%m-%d')
        )
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
