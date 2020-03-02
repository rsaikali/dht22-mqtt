#!/usr/bin/env python
import os
import time
import psutil
import adafruit_dht
import paho.mqtt.publish as publish

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(name)s] %(levelname)8s %(message)s')


# Config from environment (see Dockerfile)
DHT22_PIN = int(os.getenv('DHT22_PIN', '4'))
DHT22_CHECK_EVERY = int(os.getenv('DHT22_CHECK_EVERY', 10))
MQTT_SERVICE_HOST = os.getenv('MQTT_SERVICE_HOST', 'mosquitto.local')
MQTT_SERVICE_PORT = int(os.getenv('MQTT_SERVICE_PORT', 1883))
MQTT_SERVICE_TOPIC = os.getenv('MQTT_SERVICE_TOPIC', 'home/livingroom')
MQTT_CLIENT_ID = os.getenv('HOSTNAME', 'dht22-mqtt-service')

logger = logging.getLogger(MQTT_CLIENT_ID)


def kill_libgpiod_pulsei():
    for proc in psutil.process_iter():
        if proc.name() == "libgpiod_pulsein":
            proc.kill()


if __name__ == "__main__":

    # Display config on startup
    logger.debug("#" * 80)
    logger.debug(f"# {DHT22_PIN=}")
    logger.debug(f"# {DHT22_CHECK_EVERY=}")
    logger.debug(f"# {MQTT_SERVICE_HOST=}")
    logger.debug(f"# {MQTT_SERVICE_PORT=}")
    logger.debug(f"# {MQTT_SERVICE_TOPIC=}")
    logger.debug(f"# {MQTT_CLIENT_ID=}")
    logger.debug("#" * 80)
    logger.info(f"Waiting a few seconds before initializing DHT22 on pin {DHT22_PIN}...")
    time.sleep(DHT22_CHECK_EVERY)

    while True:

        try:
            # Initializes DHT22 on given GPIO pin
            dht22_sensor = adafruit_dht.DHT22(DHT22_PIN)

            # Read from sensor
            temperature = dht22_sensor.temperature
            humidity = dht22_sensor.humidity

            # 100% CPU use of libgpiod_pulsein on Raspberry Pi
            # https://github.com/adafruit/Adafruit_Blinka/issues/210
            kill_libgpiod_pulsei()
            del dht22_sensor
        except RuntimeError as e:
            kill_libgpiod_pulsei()
            del dht22_sensor
            logger.error(str(e))
            # Measure is wrong just after an error
            # https://github.com/adafruit/Adafruit_CircuitPython_DHT/pull/31
            # https://github.com/adafruit/Adafruit_Blinka/issues/210#issuecomment-578470762
            time.sleep(DHT22_CHECK_EVERY)
            continue

        # Prepare messages to be published on MQTT
        logger.info(f"[{MQTT_SERVICE_TOPIC}/temperature] --- {temperature}°C ---> [{MQTT_SERVICE_HOST}:{MQTT_SERVICE_PORT}]")
        logger.info(f"[{MQTT_SERVICE_TOPIC}/humidity] ------ {humidity}% ----> [{MQTT_SERVICE_HOST}:{MQTT_SERVICE_PORT}]")

        msgs = [
            {
                'topic': f"{MQTT_SERVICE_TOPIC}/temperature",
                'payload': str(temperature)
            },
            {
                'topic': f"{MQTT_SERVICE_TOPIC}/humidity",
                'payload': str(humidity)
            }
        ]

        try:
            # Publish messages on given MQTT broker
            publish.multiple(msgs, hostname=MQTT_SERVICE_HOST, port=MQTT_SERVICE_PORT, client_id=MQTT_CLIENT_ID)
        except Exception:
            logger.error("An error occured publishing values to MQTT", exc_info=True)

        # Sleep a little
        time.sleep(DHT22_CHECK_EVERY)
