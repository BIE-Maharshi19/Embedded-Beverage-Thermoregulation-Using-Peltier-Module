# Siploma

A smart IoT-based beverage temperature control system that allows users to heat or chill drinks to their desired temperature using a web interface. The system integrates a Raspberry Pi, AWS IoT Core, and MongoDB to manage real-time control and analytics.

## Team 9

- Janice Uwujaren  
- Maharshi Patel  
- Misha Hemant Joshi  
- Rohan Vitthal Dhamale  

## Project Structure

```text
siploma-smart/                         # Root of the Siploma Smart Beverage Control System project
├── dashboard/                         # Web app frontend (Flask + JavaScript)
│   └── app.py                         # Main Flask server for UI and API endpoints
│
├── hardware_code/                     # Raspberry Pi code to control heating/cooling based on MQTT messages
│   └── start.py                       # Reads temp sensor, controls Peltier, sends performance data
│
├── lambda/                            # AWS Lambda function for persisting MQTT messages into MongoDB
│   └── userInputDataToDatabase/
│       └── userInputDataToDatabase.py # Lambda handler for user input and performance topics
│
├── src/                               # Shared modules and config used across dashboard, hardware, and lambda
│   ├── certs/                         # AWS IoT Core X.509 certificates for secure MQTT communication
│   │   ├── certificate.pem.crt
│   │   ├── private.pem.key
│   │   └── AmazonRootCA1.pem
│   ├── aws_mqtt_client.py             # Reusable MQTT wrapper (if needed)
│   ├── config.py                      # Central config loader using .env file
│   └── db_client.py                   # MongoDB connection helper for reusability
│
├── requirements.txt                   # Python dependencies for the entire project
├── siploma_light.png                  # System architecture or flow diagram (light background)
├── siploma.png                        # Transparent version of the system diagram
└── README.md                          # Documentation and usage guide
```

## Setup and Usage

### 1. Add AWS IoT Certificates

To enable secure communication with AWS IoT Core, you'll need to place the required certificate files into the `src/certs/` directory.

Obtain the following 3 files (provided separately):

- `certificate.pem.crt` – Device certificate  
- `private.pem.key` – Device private key  
- `AmazonRootCA1.pem` – AWS IoT Root CA certificate  

Copy them into the `src/certs/` directory:

```text
src/certs/
├── certificate.pem.crt
├── private.pem.key
└── AmazonRootCA1.pem
```

These certificates are referenced in your `.env` file:

```ini
CERT_PATH=src/certs/certificate.pem.crt
PRIVATE_KEY_PATH=src/certs/private.pem.key
ROOT_CA_PATH=src/certs/AmazonRootCA1.pem
```

> **Do not commit these certificate files to version control.** They are sensitive and should be kept private.

---

### 2. Environment Variables

Create a `.env` file in the root with the following content:

```ini
# AWS Config
AWS_ENDPOINT=a27w9tpjjy8cdi-ats.iot.us-east-1.amazonaws.com
MQTT_PORT=8883
TOPIC_USER_INPUT="siploma/user/input"
TOPIC_PERFORMANCE="siploma/performance"
CLIENT_ID=siploma_webapp
HARDWARE_CLIENT_ID=siploma_hardware
KEEPALIVE=60
CERT_PATH=src/certs/certificate.pem.crt
PRIVATE_KEY_PATH=src/certs/private.pem.key
ROOT_CA_PATH=src/certs/AmazonRootCA1.pem

# MongoDB Config (Flask/webapp settings)
DB_USER=web_app
DB_PASSWORD=Siplomawebapp
DB_CLUSTER=UserFrequency
DB_DATABASE=Simploma
DB_COLLECTION=Performance

MONGO_URI=mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true&w=majority # example

# Lambda-specific MongoDB settings
LAMBDA_DB_USER=aws_lambda
LAMBDA_DB_PASSWORD=Siplomalambdauser
LAMBDA_DB_DATABASE=Siploma
LAMBDA_DB_CLUSTER=UserFrequency
LAMBDA_DB_COLLECTION=UserInput
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run the Web Dashboard

Start the Flask web server:

```bash
python dashboard/app.py
```

This launches the real-time analytics and control dashboard on `localhost:5000`.

---

### 5. Raspberry Pi Hardware Code

Inside `hardware_code/`, you'll find `start.py` which:

- Reads drink temperature via a DS18B20 sensor  
- Controls a Peltier module via GPIO  
- Subscribes to MQTT messages for target temperature  

Make sure you connect:

- DS18B20 sensor  
- Peltier module + MOSFET + 12V PSU  
- GPIO pins 17 (heat) and 18 (cool)  

---

### 6. AWS Lambda Integration

The function under `lambda/userInputDataToDatabase`:

- Listens for MQTT topic events via AWS IoT Core Rule
- Persists incoming messages into MongoDB

---

## Features

- Web dashboard to send target drink temperature  
- Real-time visualization of heating/cooling performance  
- Session-based tracking and user preferences  
- Secure communication via X.509 and TLS  
- AWS Lambda + MongoDB data logging  

---

## Security Notes

- X.509 certificate-based authentication (AWS IoT Core)  
- IP whitelisting for MongoDB Atlas  
- IAM policies scoped to required MQTT topics  
- Lambda functions run within a private VPC