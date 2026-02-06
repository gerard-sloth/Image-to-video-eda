from pymongo import MongoClient
from config.settings import settings

_client = None

def get_client():
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_uri)
    return _client

def get_collection(db_name: str, collection_name: str):
    return get_client()[db_name][collection_name]