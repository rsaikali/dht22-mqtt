# dht22-mqtt

![PEP8](https://github.com/rsaikali/dht22-mqtt/workflows/PEP8/badge.svg)
![Docker](https://github.com/rsaikali/dht22-mqtt/workflows/Docker/badge.svg)

`dht22-mqtt` is a Python script to get temperature and humidity measures published to a MQTT (message queue) broker.
Temperature and humidity are retrieved through a DHT22 sensor (connected to RaspberryPi GPIO in my case).

Measurements are retrieved using the given GPIO pin, and published into MQTT broker given the topic, host and port you have configured.

## Hardware needed

This project needs a DHT22 temperature and humidity sensor connected to a RaspberryPi.
Many examples are available on Google on how to plug the sensor to RaspberryPi GPIO pins.

<p align="center">
    <img src="https://img3.bgxcdn.com/thumb/large/2014/xiemeijuan/07/SKU146979/SKU146979a.jpg" width="200" height="200">
    <img src="https://www.elektor.fr/media/catalog/product/cache/2b4bee73c90e4689bbc4ca8391937af9/r/a/raspberry-pi-4-4gb.jpg" width="200" height="200">
</p>

Please note that I'll use the GPIO pin 4 in the following chapters.

## How to use it?

`dht22-mqtt` can be used as a standalone Python script or as a Docker container.

### Use as a standalone script

Install Linux requirements on RaspberryPi:

```sh
apt-get update
apt-get install --no-install-recommends -y libgpiod2 gcc build-essential
```

Git clone the project:

```sh
git clone https://github.com/rsaikali/dht22-mqtt.git
cd dht22-mqtt
```

Install Python requirements:

```sh
pip3 install -r requirements.txt
```

Configure through environment variables (those are default values if nothing given):

```sh
# Which Raspberry GPIO pin to use
export DHT22_PIN=4
# How many seconds between measures
export DHT22_CHECK_EVERY=10

# MQTT broker host
export MQTT_SERVICE_HOST=mosquitto.local
# MQTT broker port
export MQTT_SERVICE_PORT=1883
# MQTT broker user - optional
export MQTT_SERVICE_USER=mqtt_user
# MQTT broker password - optional
export MQTT_SERVICE_PASSWORD=very_strong_password
 
# MQTT broker topic to publish measures
export MQTT_SERVICE_TOPIC=home/livingroom
# MQTT client ID (default will be the hostname)
export MQTT_CLIENT_ID=dht22-mqtt-service
```

If you do not set user and password environment variables, auth is not used. 

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

Needed environment is obviously the same as the standalone script mechanism, described in the Dockerfile:

Please note that you'll need to use `--privileged` when running Docker to have access to GPIO.

```sh
docker run --name dht22-mqtt \
           --privileged \
           --restart=always \
           --net=host \
           -tid \
           -e DHT22_PIN=4 \
           -e DHT22_CHECK_EVERY=10 \
           -e MQTT_SERVICE_HOST=mosquitto.local \
           -e MQTT_SERVICE_PORT=1883 \
           -e MQTT_SERVICE_USER=mqtt_user \
           -e MQTT_SERVICE_PASSWORD=very_strong_password \           
           -e MQTT_SERVICE_TOPIC=home/livingroom \
           -e MQTT_CLIENT_ID=dht22-mqtt-service \
           rsaikali/dht22-mqtt
```

#### Build your own Docker image

To build an `linux/arm/v7` docker image from another architecture, you'll need a special (experimental) Docker multi-architecture build functionality detailled here: [Building Multi-Arch Images for Arm and x86 with Docker Desktop](https://www.docker.com/blog/multi-arch-images/)

You'll basically need to activate experimental features and use `buildx`.

```sh
export DOCKER_CLI_EXPERIMENTAL=enabled
docker buildx create --use --name build --node build --driver-opt network=host
docker buildx build --platform linux/arm/v7 -t <your-repo>/dht22-mqtt --push .
```

## Known issues

DHT22 sensor is not extremely reliable, you'll sometimes find errors in log, those are not a big deal, as it will retry by itself.

```
2020-02-16 11:05:00 [dht22-mqtt-service] [+] [home/livingroom/temperature] --- 22.7°C ---> [mosquitto.local:1883]
2020-02-16 11:05:00 [dht22-mqtt-service] [+] [home/livingroom/humidity] ------ 56.6% ----> [mosquitto.local:1883]
2020-02-16 11:05:10 [dht22-mqtt-service] [-] An error occured while getting DHT22 measure
2020-02-16 11:05:10 [dht22-mqtt-service] [-] Checksum did not validate. Try again.
2020-02-16 11:05:20 [dht22-mqtt-service] [+] [home/livingroom/temperature] --- 22.9°C ---> [mosquitto.local:1883]
2020-02-16 11:05:20 [dht22-mqtt-service] [+] [home/livingroom/humidity] ------ 56.8% ----> [mosquitto.local:1883]
```

When running, a required library may take 100% CPU or return bad reading, those are known bugs with issues in progress:

* [adafruit/Adafruit_Blinka: 100% CPU use of libgpiod_pulsein on Raspberry Pi](https://github.com/adafruit/Adafruit_Blinka/issues/210)
* [adafruit/Adafruit_CircuitPython_DHT: Improve error handling](https://github.com/adafruit/Adafruit_CircuitPython_DHT/pull/31)

```
top - 11:10:00 up 12:27,  1 user,  load average: 2.00, 2.01, 2.03
Tasks: 130 total,   3 running, 127 sleeping,   0 stopped,   0 zombie
%Cpu(s):  9.0 us, 18.0 sy,  0.0 ni, 72.9 id,  0.0 wa,  0.0 hi,  0.1 si,  0.0 st
MiB Mem :   3854.5 total,   3134.0 free,    222.5 used,    498.0 buff/cache
MiB Swap:      0.0 total,      0.0 free,      0.0 used.   3521.4 avail Mem

  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND
11407 root      rt   0    1496    340    284 R 100.0   0.0  43:56.08 libgpiod_pulsei
    9 root      20   0       0      0      0 S   0.4   0.0   0:02.95 ksoftirqd/0
```