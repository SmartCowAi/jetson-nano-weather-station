import board
import busio

import adafruit_circuitpython_hm3301

i2c = busio.I2C(board.SCL_1, board.SDA_1)
hm3301 = adafruit_circuitpython_hm3301.Seeed_HM3301_I2C(i2c)

print(hm3301.PM_1_0_conctrt_std)
