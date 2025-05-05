from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os
import json
from pymongo import MongoClient
from src.config import (
    MONGO_URI,
    DB_DATABASE,
    DB_COLLECTION,
    AWS_ENDPOINT,
    CLIENT_ID,
    ROOT_CA_PATH,
    PRIVATE_KEY_PATH,
    CERT_PATH,
    TOPIC_USER_INPUT
)

# MongoDB Setup
user_input_col = None
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = mongo_client[DB_DATABASE]
    user_input_col = db[DB_COLLECTION]
    print("Connected to MongoDB.")
except Exception as e:
    print("MongoDB connection failed:", str(e))
    user_input_col = None

# MQTT Setup
mqtt_client = None
try:
    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
    mqtt_client = AWSIoTMQTTClient(CLIENT_ID)
    mqtt_client.configureEndpoint(AWS_ENDPOINT, 8883)
    mqtt_client.configureCredentials(ROOT_CA_PATH, PRIVATE_KEY_PATH, CERT_PATH)
    mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
    mqtt_client.configureOfflinePublishQueueing(-1)
    mqtt_client.configureDrainingFrequency(2)
    mqtt_client.configureConnectDisconnectTimeout(30)
    mqtt_client.configureMQTTOperationTimeout(5)
    mqtt_client.connect()
    print("MQTT client connected.")
except Exception as e:
    print("MQTT not configured properly:", str(e))

# Flask Setup
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/api/set-temp', methods=['POST'])
def set_temp():
    try:
        data = request.get_json()
        print("Received set-temp:", data)

        target_temp = int(data.get("target_temp"))
        session_id = f"session_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

        message = {
            "timestamp": datetime.utcnow().isoformat(),
            "target_temp": target_temp,
            "session_id": session_id,
            "user_action": "SET",
            "source": "webapp"
        }

        mqtt_client.publish(TOPIC_USER_INPUT, json.dumps(message), 1)
        return jsonify({"message": "Target temperature received", "session_id": session_id}), 200

    except Exception as e:
        print("Error in /api/set-temp:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route('/api/user-inputs')
def get_user_inputs():
    try:
        if user_input_col is None:
            return jsonify({"error": "MongoDB connection not available"}), 503

        records = list(user_input_col.find().sort([("_id", -1)]).limit(100))
        print(f"Records fetched: {len(records)}")

        output = []
        for r in records:
            parsed = {
                "session_id": r.get("session_id", "N/A"),
                "user_action": r.get("user_action", ""),
                "mode": r.get("mode", ""),
                "uuid": r.get("uuid", ""),
                "timestamp": r.get("timestamp"),
                "drink_temp": r.get("drink_temp", 0),
                "target_temp": r.get("target_temp", 0),
                "ambient_temp": r.get("ambient_temp", 0),
                "source": r.get("source", "unknown")
            }
            print(parsed)
            output.append(parsed)

        return jsonify(list(reversed(output)))

    except Exception as e:
        print("Error in /api/user-inputs:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
