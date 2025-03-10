import pymongo
import os
from pymongo import MongoClient
import requests
from module_3 import get_thumbnail_caption
import hashlib
from module_5 import check_duplicates

def store_data():
    client = MongoClient('localhost', 27017)
    db = client.Assignment_1
    articles_col = db.articles
    data = get_thumbnail_caption()
    os.makedirs("thumbnails", exist_ok=True)
    for entry in data:
        if entry["thumbnail"] != "No image found" and entry["title"] != "No title found" and not check_duplicates(entry):
            image_hash = hashlib.md5(entry["thumbnail"].encode()).hexdigest()
            image_path = f"thumbnails/{image_hash}.jpg"
            with open(image_path, "wb") as f:
                f.write(requests.get(entry["thumbnail"]).content)
            entry["image_path"] = image_path
            del entry["thumbnail"]
            articles_col.insert_one(entry)
    print("Database updated successfully!")