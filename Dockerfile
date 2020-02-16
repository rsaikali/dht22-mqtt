FROM python:3.8-slim-buster

ENV DHT22_PIN 4
ENV DHT22_CHECK_EVERY 10

ENV MQTT_SERVICE_HOST mosquitto.local
ENV MQTT_SERVICE_PORT 1883
ENV MQTT_SERVICE_TOPIC home/livingroom
ENV MQTT_CLIENT_ID dht22-mqtt-service

RUN apt-get update && \
    apt-get install --no-install-recommends -y libgpiod2 gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY dht22-mqtt.py .

ENTRYPOINT ["python", "./dht22-mqtt.py"]