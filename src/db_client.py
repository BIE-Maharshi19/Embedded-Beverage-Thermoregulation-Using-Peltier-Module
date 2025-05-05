from pymongo import MongoClient
from src import config

def get_db_collection():
    """Connect to MongoDB and return the specified collection."""
    try:
        client = MongoClient(config.MONGO_URI)
        db = client[config.DB_DATABASE]
        collection = db[config.DB_COLLECTION]
        return collection
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        return None
