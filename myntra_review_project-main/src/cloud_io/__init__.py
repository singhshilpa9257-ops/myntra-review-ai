# src/cloud_io/__init__.py
import pandas as pd
from pymongo import MongoClient
import os
from src.constants import MONGO_DATABASE_NAME
from src.exception import CustomException
import sys


class MongoIO:
    
    def __init__(self):
        try:
            mongo_db_url = os.getenv("MONGO_DB_URL")
            if not mongo_db_url:
                mongo_db_url = "mongodb+srv://imran:TdPLW9Ad0OzpSSD2@cluster0.fv0lm61.mongodb.net/?retryWrites=true&w=majority"
            
            self.client = MongoClient(mongo_db_url)
            self.db = self.client[MONGO_DATABASE_NAME]
            self.db_name = MONGO_DATABASE_NAME
        except Exception as e:
            raise CustomException(e, sys)

    def store_reviews(self, product_name: str, reviews: pd.DataFrame):
        try:
            collection_name = product_name.replace(" ", "_")
            collection = self.db[collection_name]
            
            records = reviews.to_dict('records')
            if records:
                collection.insert_many(records)
            print(f"✅ Stored {len(records)} reviews for {product_name}")
        except Exception as e:
            raise CustomException(e, sys)

    def get_reviews(self, product_name: str):
        try:
            collection_name = product_name.replace(" ", "_")
            collection = self.db[collection_name]
            data = list(collection.find({}, {"_id": 0}))
            return pd.DataFrame(data) if data else pd.DataFrame()
        except Exception as e:
            raise CustomException(e, sys)