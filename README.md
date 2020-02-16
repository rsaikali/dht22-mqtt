# dht22-mqtt

`dht22-mqtt` is a Python script to get temperature and humidity measures published to a MQTT (message queue) broker.
Temperature and humidity are retrieved through a DHT22 sensor (connected to RaspberryPi GPIO in my case).

Measurements are retrieved using the given GPIO pin, and published into configure MQTT broker given the topic, host and port you have configured.

## Hardware needed

You'll need a DHT22 temperature and humidity sensor attached to your RaspberryPi.
Many examples are available on Google on how to plug the sensor to GPIO pins.

<p align="center"><img src="https://img3.bgxcdn.com/thumb/large/2014/xiemeijuan/07/SKU146979/SKU146979a.jpg" width="200" height="200"></p>

Please note that I'll use the GPIO pin 4 in the following chapters.

## How to use it?

`dht22-mqtt` can be used as a standalone Python script or a Docker container.

### Use as a standalone script

Install Linux requirements:

```sh
apt-get update
apt-get install --no-install-recommends -y libgpiod2 gcc build-essential
```

Install Python requirements:

```sh
pip3 install --no-cache-dir -r requirements.txt
```

Configure through environment variables:

```sh
# Which Raspberry GPIO pin to use
export DHT22_PIN=4
# How many seconds between measures
export DHT22_CHECK_EVERY=10

# MQTT broker host
export MQTT_SERVICE_HOST=mosquitto.local
# MQTT broker port
export MQTT_SERVICE_PORT=1883
# MQTT broker topic to publish measures
export MQTT_SERVICE_TOPIC=home/livingroom
# MQTT client ID
export MQTT_CLIENT_ID=dht22-mqtt-service
```

Launch application:

```sh
python ./dht22-mqtt.py
```

You should see output printed:
```sh
(...)
2020-02-16 10:57:50 [dht22-mqtt-service] [+] [home/livingroom/temperature] --- 20.7°C ---> [mosquitto.local:1883]
2020-02-16 10:57:50 [dht22-mqtt-service] [+] [home/livingroom/humidity] ------ 55.7% ----> [mosquitto.local:1883]
2020-02-16 10:58:00 [dht22-mqtt-service] [+] [home/livingroom/temperature] --- 20.9°C ---> [mosquitto.local:1883]
2020-02-16 10:58:00 [dht22-mqtt-service] [+] [home/livingroom/humidity] ------ 55.8% ----> [mosquitto.local:1883]
(...)
```

### Use as Docker container

#### Use Docker hub image

An image is available on Docker Hub: [rsaikali/dht22-mqtt](https://hub.docker.com/r/rsaikali/dht22-mqtt)

```sh
docker pull rsaikali/dht22-mqtt
```

Needed environment is obviously the same as the standalone script mechanism, described in the Dockerfile:

```sh
ENV DHT22_PIN 4
ENV DHT22_CHECK_EVERY 10

ENV MQTT_SERVICE_HOST mosquitto.local
ENV MQTT_SERVICE_PORT 1883
ENV MQTT_SERVICE_TOPIC home/livingroom
ENV MQTT_CLIENT_ID dht22-mqtt-service
```

#### Build your own Docker image

To build an `arm` docker image from another architecture, you'll need a special Docker multi-architecture build functionality detailled [here](https://community.arm.com/developer/tools-software/tools/b/tools-software-ides-blog/posts/getting-started-with-docker-for-arm-on-linux).

You'll basically need to activate experimental features and use `buildx`.

```sh
export DOCKER_CLI_EXPERIMENTAL=enabled
docker buildx create --use --name build --node build --driver-opt network=host
docker buildx build --platform linux/arm/v7 -t <your-repo>/dht22-mqtt .
```

