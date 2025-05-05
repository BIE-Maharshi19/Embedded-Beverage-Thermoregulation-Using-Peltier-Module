from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import json
from pymongo.errors import OperationFailure

from src.config import (
    TOPIC_USER_INPUT,
    TOPIC_PERFORMANCE,
    LAMBDA_DB_USER,
    LAMBDA_DB_PASSWORD,
    LAMBDA_DB_DATABASE,
    LAMBDA_DB_CLUSTER,
    LAMBDA_DB_COLLECTION
)

def lambda_handler(event, context):
    uri = f'mongodb+srv://{LAMBDA_DB_USER}:{LAMBDA_DB_PASSWORD}@{LAMBDA_DB_CLUSTER.lower()}.v1lt2ix.mongodb.net/?appName={LAMBDA_DB_CLUSTER}'
    try:
        # Create a new client and connect to the server
        client = MongoClient(uri, server_api=ServerApi('1'))
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
        
        if event.get('topic') == TOPIC_USER_INPUT:
            session_id = event.get('session_id')
            target_temp = event.get('target_temp')
            timestamp = event.get('timestamp')
            source = event.get('source')

            database = client[LAMBDA_DB_DATABASE]
            collection = database[LAMBDA_DB_COLLECTION]
            collection.insert_one({
                "timestamp" : timestamp,
                "session_id": session_id,
                "target_temp": target_temp,
                "source": source
            })
        elif event.get('topic') == TOPIC_PERFORMANCE:
            session_id = event.get('session_id')
            action = event.get('user_action')
            mode = event.get('mode')
            timestamp = event.get('timestamp')
            current_temp = event.get('drink_temp')
            target_temp = event.get('target_temp')
            source = event.get('source')

            database = client[LAMBDA_DB_DATABASE]
            collection = database[TOPIC_PERFORMANCE]
            if action == "SET":
                collection.insert_one({
                    "session_id": session_id,
                    "user_action": action,
                    "mode": mode,
                    "timestamp": timestamp,
                    "drink_temp": current_temp,
                    "target_temp": target_temp,
                    "source": source
                })
            elif action == "STOP":
                collection.insert_one({
                    "session_id": session_id,
                    "user_action": action,
                    "mode": mode,
                    "timestamp": timestamp,
                    "source": source
                })
        return {
            'statusCode': 200,
            'body': json.dumps('Insertion Successful!')
        }
    except OperationFailure as e:
        if e.code == 8000:
            return {
                'statusCode': 401,
                'body': json.dumps('Authentication Failed')
            }