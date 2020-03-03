###################
# Build environment to get fresh libgpiod_pulsein
# See also: https://github.com/adafruit/libgpiod_pulsein/pull/1
#           https://github.com/adafruit/Adafruit_Blinka/issues/210
FROM python:3.8-slim-buster AS builder

RUN apt-get update && \
    apt-get install --no-install-recommends -y libgpiod2 libgpiod-dev git gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN git clone https://github.com/michaellass/libgpiod_pulsein.git && \
    cd /opt/libgpiod_pulsein && \
    git checkout cpu-fix && \
    cd src && \
    make

########################
# Production environment
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

WORKDIR /opt

COPY requirements.txt /opt/requirements.txt

RUN pip3 install --no-cache-dir -r /opt/requirements.txt

COPY --from=builder /opt/libgpiod_pulsein/src/libgpiod_pulsein /usr/local/lib/python3.8/site-packages/adafruit_blinka/microcontroller/bcm283x/pulseio/libgpiod_pulsein

COPY dht22-mqtt.py /opt/dht22-mqtt.py

ENTRYPOINT ["python", "/opt/dht22-mqtt.py"]