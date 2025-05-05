# Instant Drink Heater & Chiller

This project implements an IoT-based drink temperature control system using a Raspberry Pi, Peltier module, and temperature sensors. It communicates via MQTT with AWS IoT Core and enables users to heat or chill drinks to a specified target temperature through cloud commands.

---

## Table of Contents

- [Overview](#overview)
- [Environment Settings](#environment-settings)
- [How to Run](#how-to-run)
- [How to Interpret Results](#how-to-interpret-results)
- [Sample Input and Output](#sample-input-and-output)
- [Additional Information](#additional-information)

---

## Overview

The system subscribes to a topic on AWS IoT Core, receives target temperature, then controls the Peltier device accordingly. Temperature readings are logged and published back to another MQTT topic with session metadata.

---

## Environment Settings

### Hardware Components

- Raspberry Pi (tested on Pi 4/5)
- DS18B20 Temperature Sensor (1-Wire)
- Peltier Module with Heatsink & Fan
- IRF520 MOSFET Relay Module
- GPIO Pin 17: Heating Control
- GPIO Pin 18: Cooling Control

### Software Dependencies

- Python 3.x
- [gpiozero](https://gpiozero.readthedocs.io/)
- [paho-mqtt](https://pypi.org/project/paho-mqtt/)

Install dependencies using pip:

```bash
pip install paho-mqtt gpiozero
```

### Environment Variables

Set the following environment variables before running the script:

```bash
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

## How to Run

Ensure all hardware is connected and powered. Then run the Python script:

```bash
python start.py
```

Upon successful connection to AWS IoT Core, the device subscribes to the input topic and awaits instructions.

---

## How to Interpret Results

1. **Received Input**: The device listens for a JSON message containing:
   - `target_temp`: Desired drink temperature
   - `session_id`: Unique session identifier
   - `source`: User or client ID

2. **System Behavior**:
   - Begins heating or cooling depending on current temperature and target.
   - Publishes two messages to the `siploma/performance` topic:
     - `SET`: Indicates start of heating/cooling
     - `STOP`: Indicates the temperature reached the desired range

3. **Sample Logs**:
   ```
   Connected to AWS IOT
   Subscribed to siploma/user/input
   Input Received
   Cold! Heating Peltier ON. Current: 21.53°C, Target: 24.00°C
   Published to siploma/performance: {...}
   ```

---

## Sample Input and Output

### Input (JSON via MQTT: `siploma/user/input`)

```json
{
  "target_temp": 18,
  "session_id": "abc123",
  "source": "webapp"
}
```

### Output (Published to MQTT: `siploma/performance`)

```json
{
  "session_id": "abc123",
  "user_action": "SET",
  "mode": "HEATING",
  "timestamp": "2025-04-13 15:40:05",
  "drink_temp": 16.5,
  "target_temp": 18.0,
  "source": "webapp"
}
```

```json
{
  "session_id": "abc123",
  "user_action": "STOP",
  "mode": "HEATING",
  "timestamp": "2025-04-13 15:42:55",
  "source": "webapp"
}
```

---

## Additional Information

- The code uses GPIO 17 for heating and GPIO 18 for cooling.
- TLS certificates are required to connect to AWS IoT Core over MQTT (port 8883).
- Temperature data is read from the DS18B20 via `/sys/bus/w1/devices/28*/w1_slave`.
- Ensure the 1-Wire interface is enabled on your Raspberry Pi (`raspi-config` > Interfaces > 1-Wire).

---
