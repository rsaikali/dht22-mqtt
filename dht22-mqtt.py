import logging
import os
import time
from pathlib import Path

import adafruit_dht
import paho.mqtt.publish as publish

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s] %(levelname)8s %(message)s')


# Config from environment (see Dockerfile)
DHT22_PIN = int(os.getenv('DHT22_PIN', '4'))
DHT22_CHECK_EVERY = int(os.getenv('DHT22_CHECK_EVERY', 1))
MQTT_SERVICE_HOST = os.getenv('MQTT_SERVICE_HOST', 'mosquitto.local')
MQTT_SERVICE_PORT = int(os.getenv('MQTT_SERVICE_PORT', 1883))
MQTT_SERVICE_USER = os.getenv('MQTT_SERVICE_USER', None)
MQTT_SERVICE_PASSWORD = os.getenv('MQTT_SERVICE_PASSWORD', None)
MQTT_SERVICE_TOPIC = os.getenv('MQTT_SERVICE_TOPIC', 'home/livingroom')
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', 'dht22-mqtt-service')

logger = logging.getLogger(MQTT_CLIENT_ID)


if __name__ == "__main__":

    # Display config on startup
    logger.debug("#" * 80)
    logger.debug(f"# {DHT22_PIN=}")
    logger.debug(f"# {DHT22_CHECK_EVERY=}")
    logger.debug(f"# {MQTT_SERVICE_HOST=}")
    logger.debug(f"# {MQTT_SERVICE_PORT=}")
    logger.debug(f"# {MQTT_SERVICE_USER=}")
    logger.debug(f"# {MQTT_SERVICE_PASSWORD=}")
    logger.debug(f"# {MQTT_SERVICE_TOPIC=}")
    logger.debug(f"# {MQTT_CLIENT_ID=}")
    logger.debug("#" * 80)

    MQTT_SERVICE_AUTH = None

    if MQTT_SERVICE_USER != None:
        MQTT_SERVICE_AUTH = {'username':MQTT_SERVICE_USER, 'password':MQTT_SERVICE_PASSWORD}


    # Initializes DHT22 on given GPIO pin
    dht22_sensor = adafruit_dht.DHT22(DHT22_PIN)

    while True:

        try:
            # Read from sensor
            temperature = dht22_sensor.temperature
            humidity = dht22_sensor.humidity
            # Touch file every time data is read (used for liveness probe in k8s)
            Path('.dht22_updated').touch()
        except RuntimeError as e:
            logger.error(str(e))
            time.sleep(5)
            continue

        logger.info(f"[{MQTT_SERVICE_TOPIC}/temperature] --- {temperature}°C ---> [{MQTT_SERVICE_HOST}:{MQTT_SERVICE_PORT}]")
        logger.info(f"[{MQTT_SERVICE_TOPIC}/humidity] ------ {humidity}% ----> [{MQTT_SERVICE_HOST}:{MQTT_SERVICE_PORT}]")

        try:
            # Prepare messages to be published on MQTT
            msgs = [(f"{MQTT_SERVICE_TOPIC}/temperature", str(temperature)),
                    (f"{MQTT_SERVICE_TOPIC}/humidity", str(humidity))]

            # Publish messages on given MQTT broker
            publish.multiple(msgs, hostname=MQTT_SERVICE_HOST, port=MQTT_SERVICE_PORT, client_id=MQTT_CLIENT_ID, auth=MQTT_SERVICE_AUTH)
        except Exception:
            logger.error("An error occured publishing values to MQTT", exc_info=True)

        # Sleep a little
        time.sleep(DHT22_CHECK_EVERY)
