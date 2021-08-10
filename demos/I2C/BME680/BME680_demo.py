#
# Modified by Ryan Agius for SmartCow AI Technologies Limited
# For use with the Seeed Grove BME680 module on I2C bus 0
#

# SPDX-FileCopyrightText: 2021 Carter Nelson for Adafruit Industries
# SPDX-License-Identifier: MIT

import time
import board
import busio
import adafruit_bme680

# Create sensor object, communicating over the board's I2C Bus 0
i2c_bus = busio.I2C(board.SCL_1, board.SDA_1)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c_bus, address=0x76)

# change this to match the location's pressure (hPa) at sea level
bme680.sea_level_pressure = 1016.40

# You will usually have to add an offset to account for the temperature of
# the sensor. This is usually around 5 degrees but varies by use. Use a
# separate temperature sensor to calibrate this one.
temperature_offset = -5

print("Seeed BME680 Temperature, Humidity, Pressure & Gas Sensor Demo")
print("Press CTRL+C to exit")
print()

while True:
    
    print("Temperature: %0.1f C" % (bme680.temperature + temperature_offset))
    print("Gas: %d ohm" % bme680.gas)
    print("Humidity: %0.1f %%" % bme680.relative_humidity)
    print("Pressure: %0.3f hPa" % bme680.pressure)
    print("Altitude = %0.2f meters" % bme680.altitude)
    print()

    time.sleep(1)
