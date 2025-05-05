# MQTT Client Setup using AWS IoT Device SDK for Python
# Reference: https://github.com/aws/aws-iot-device-sdk-python

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from src import config

client = AWSIoTMQTTClient(config.CLIENT_ID)

client.configureEndpoint(config.AWS_ENDPOINT, 8883)

client.configureCredentials(
    config.ROOT_CA_PATH,
    config.PRIVATE_KEY_PATH,
    config.CERT_PATH
)

client.configureOfflinePublishQueueing(-1)    # Infinite offline Publish queueing
client.configureDrainingFrequency(2)          # Draining: 2 Hz
client.configureConnectDisconnectTimeout(10)  # in seconds
client.configureMQTTOperationTimeout(5)       # in seconds

client.connect()
