import os
import sys
import glob
import time
import json
import ssl
from gpiozero import OutputDevice
import paho.mqtt.client as mqtt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config import (
    AWS_ENDPOINT,
    CERT_PATH,
    HARDWARE_CLIENT_ID,
    PRIVATE_KEY_PATH,
    ROOT_CA_PATH,
    TOPIC_USER_INPUT,
    TOPIC_PERFORMANCE
)

# Setup heating and cooling pins
heat_pin = OutputDevice(17)  # GPIO pin for heating
cool_pin = OutputDevice(18)  # GPIO pin for cooling (changed from 17 to avoid conflict)

# Mount temperature sensor
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
topic = TOPIC_USER_INPUT

def read_temp_raw():
    with open(device_file, 'r') as f:
        lines = f.readlines()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

def control_peltier(current_temp, target_temp, tolerance):
    if current_temp < target_temp - tolerance:
        print(f"Cold! Heating Peltier ON. Current: {current_temp:.2f}°C, Target: {target_temp}°C")
        heat_pin.on()
        cool_pin.off()
        return "heating"
    elif current_temp > target_temp + tolerance:
        print(f"Warm! Cooling Peltier ON. Current: {current_temp:.2f}°C, Target: {target_temp}°C")
        heat_pin.on()
        # heat_pin.off()
        return "cooling"
    else:
        print(f"Temperature within tolerance. Peltier OFF. Current: {current_temp:.2f}°C, Target: {target_temp}°C")
        heat_pin.off()
        # cool_pin.off()
        return "off"

def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker with result code ' + str(rc))
    if rc == 0:
        client.subscribe(topic)
        print(f"Subscribed to {topic}")

def on_message(client, userdata, msg):
    if msg.topic == topic:
        print("Input Received")
        try:
            input_message = json.loads(msg.payload.decode())
            target_temp = float(input_message["target_temp"])
            tolerance = float(input_message.get("tolerance", 0.5))
            session_id = input_message["session_id"]
            source = input_message["source"]
            
            current_temp = read_temp()

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            if target_temp > current_temp - tolerance:
                action = "HEATING"
            elif target_temp < current_temp + tolerance:
                action = "COOLING"
            else:
                action = "off"
            if action != "off":
                performance_msg = json.dumps({
                    "session_id": session_id,
                    "user_action": "SET",
                    "mode": action,
                    "timestamp": timestamp,
                    "drink_temp": current_temp,
                    "target_temp": target_temp,
                    "source": source
                })
                performance_topic = TOPIC_PERFORMANCE
                mqtt_client.publish(performance_topic, performance_msg)

            while control_peltier(current_temp, target_temp, tolerance) != "off":
                time.sleep(1)
                current_temp = read_temp()
            
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            
            performance_msg = json.dumps({
                "session_id": session_id,
                "user_action": "STOP",
                "mode": action,
                "timestamp": timestamp,
                "source" : source
            })
            mqtt_client.publish(performance_topic, performance_msg)
            print(f"Published to {performance_topic}: {performance_msg}")
            print(f"Current Temperature: {current_temp:.2f}")
            
        except json.JSONDecodeError:
            print("Error: Invalid JSON in message payload")
        except KeyError:
            print("Error: Missing 'target_temp' in message payload")
        except ValueError:
            print("Error: Invalid temperature value")

# Setup MQTT client
mqtt_client = mqtt.Client(client_id=HARDWARE_CLIENT_ID)
mqtt_client.tls_set(ROOT_CA_PATH, 
                    certfile=CERT_PATH, 
                    keyfile=PRIVATE_KEY_PATH, 
                    tls_version=ssl.PROTOCOL_TLSv1_2)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

# Connect to AWS IoT Core
mqtt_client.connect(AWS_ENDPOINT, 8883, 60)
print('Connected to AWS IOT')

try:
    print('Starting MQTT loop...')
    mqtt_client.loop_forever()
except KeyboardInterrupt:
    print("\nStopped by user. Cleaning up...")
finally:
    heat_pin.off()
    cool_pin.off()
    heat_pin.close()
    cool_pin.close()
    mqtt_client.disconnect()
    print("Cleanup complete. Exiting.")