import os
from dotenv import load_dotenv

load_dotenv()

# AWS IoT Core Configuration
AWS_ENDPOINT = os.getenv("AWS_ENDPOINT")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
TOPIC_USER_INPUT = os.getenv("TOPIC_USER_INPUT")
TOPIC_PERFORMANCE = os.getenv("TOPIC_PERFORMANCE")
CLIENT_ID = os.getenv("CLIENT_ID")
HARDWARE_CLIENT_ID = os.getenv("HARDWARE_CLIENT_ID")
KEEPALIVE = int(os.getenv("KEEPALIVE", 60))

CERT_PATH = os.getenv("CERT_PATH")
PRIVATE_KEY_PATH = os.getenv("PRIVATE_KEY_PATH")
ROOT_CA_PATH = os.getenv("ROOT_CA_PATH")

# MongoDB Configuration (for web/dashboard)
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_CLUSTER = os.getenv("DB_CLUSTER")
DB_DATABASE = os.getenv("DB_DATABASE")
DB_COLLECTION = os.getenv("DB_COLLECTION")
MONGO_URI = os.getenv("MONGO_URI")

# Lambda-specific MongoDB (optional override)
LAMBDA_DB_USER = os.getenv("LAMBDA_DB_USER")
LAMBDA_DB_PASSWORD = os.getenv("LAMBDA_DB_PASSWORD")
LAMBDA_DB_CLUSTER = os.getenv("LAMBDA_DB_CLUSTER")
LAMBDA_DB_DATABASE = os.getenv("LAMBDA_DB_DATABASE")
LAMBDA_DB_COLLECTION = os.getenv("LAMBDA_DB_COLLECTION")