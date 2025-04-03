-- Checking if database exists, if not create it
SELECT 'CREATE DATABASE rssfeeds'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'rssfeeds');

-- Connecting to the database
\c rssfeeds

-- Checking if table exists, if not create it
CREATE TABLE IF NOT EXISTS news_articles (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    publication_timestamp TIMESTAMP NOT NULL,
    weblink TEXT NOT NULL,
    image_path TEXT,
    tags TEXT[],
    summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Creating index for faster searches
CREATE INDEX IF NOT EXISTS idx_publication_timestamp ON news_articles(publication_timestamp);
