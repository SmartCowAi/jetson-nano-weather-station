#! /usr/bin/env bash

# Script file to automatically install packages and libraries to run the weather station peripherals
# on a Jetson Nano 2GB develoment kit

# authorise sudo with a dummy command
sudo echo

#install necessary packages
sudo apt-get update
sudo apt-get -y install python3-pip
sudo apt-get -y install libjpeg-dev zlib1g-dev
sudo apt-get -y install libfreetype6-dev

# install python libraries
pip3 install --upgrade Jetson.GPIO
pip3 install --upgrade adafruit-blinka
pip3 install --upgrade pynmea2
pip3 install --upgrade adafruit-circuitpython-bme680
pip3 install --upgrade adafruit-circuitpython-ssd1306
pip3 install --upgrade freetype-py
pip3 install --upgrade Pillow
