# jetson-nano-weather-station
An ambient weather station making use of SeeedStudio's Grove sensors, based arount Nvidia's Jetson Nano 2GB Development Kit, as documented in our blog series [here](https://medium.com/@Smartcow_ai/a-jetson-nano-ambient-weather-station-part-1-c93cae197dcf).

## Prerequisites and Library Installation

After flashing the Jetson Nano and connecting it to the internet via an ethernet cable or to a WiFi network using a [dongle](https://github.com/SmartCowAi/Jetson-WifiDongle-Drivers), open a terminal window, clone this repository and **cd** into it.
```
git clone https://github.com/SmartCowAi/jetson-nano-weather-station.git
cd jetson-nano-weather-station
```

Included in the repository is a library installation script, *library_installer.sh* to automatically download and install the linux packages and python libraries required to communicate with the station's peripherals.

```
sudo chmod +x installer.sh
sudo ./library_installer.sh
```

## Usage

### Demos

Individual programs to try out the sensors and modules can be found in the **demos/** directory. Refer to the [first blog](https://medium.com/@Smartcow_ai/a-jetson-nano-ambient-weather-station-part-1-c93cae197dcf) in our four part series for the peripheral's pinouts.
