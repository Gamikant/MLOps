import pymongo
from pymongo import MongoClient
from module_3 import get_thumbnail_caption

def check_duplicates(article):
    client = MongoClient('localhost', 27017)
    db = client.Assignment_1
    articles_col = db.articles
    return articles_col.count_documents({"title": article["title"]}) > 0