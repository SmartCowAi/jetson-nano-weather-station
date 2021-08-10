import os
import time
import subprocess

import board
import busio
import RPi.GPIO as GPIO

import serial
import pynmea2

from datetime import datetime
import time
from time import mktime

from adafruit_bme680 import Adafruit_BME680_I2C
from adafruit_ssd1306 import SSD1306_I2C
from seeed_hm3301 import HM3301_I2C
from seeed_air530 import GPS

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

OLED_WIDTH = 128
OLED_HEIGHT = 64

# pin definitions
rot_sw_pin = 'GPIO_PE6'
rot_dt_pin = 'GPIO_PZ0'
rot_clk_pin = 'CAM_AF_EN'

display_item = 0
item_length = 1
sensor_data = ['Jetson\nWeather\nStation']

read_interval = 0.05

last_acq = time.monotonic()

# Set default font dor OLED Displays
fwd = os.path.dirname(os.path.abspath(__file__))
font_default = ImageFont.truetype(fwd + '/fonts/Oswald-Medium.ttf', 16)
font_big = ImageFont.truetype(fwd + '/fonts/Oswald-Medium.ttf', 24)
font_huge = ImageFont.truetype(fwd + '/fonts/Oswald-Medium.ttf', 30)

class rotary_encoder:

    def __init__(self, sw_pin=rot_sw_pin, dt_pin=rot_dt_pin, clk_pin=rot_clk_pin):
        # pin setup
        #GPIO.setmode(GPIO.TEGRA_SOC)  # BOARD pin-numbering scheme
        GPIO.setup([sw_pin, dt_pin, clk_pin], GPIO.IN)  #rotary encoder pins set as inputs

        # Interupts setup
        GPIO.add_event_detect(sw_pin, GPIO.FALLING, callback=self.sw_isr, bouncetime=200)
        GPIO.add_event_detect(clk_pin, GPIO.FALLING, callback=self.clk_isr, bouncetime=100)
        GPIO.add_event_detect(dt_pin, GPIO.FALLING, callback=self.dt_isr, bouncetime=100)

        self.clk_int = False
        self.dt_int = False

    def sw_isr(self, channel):
        print("Switch Pressed")
    
    def clk_isr(self, channel):
        self.clk_int = True
    
        if self.dt_int:
            self.rot_isr(False)
    
    def dt_isr(self, channel):
        self.dt_int = True
    
        if self.clk_int:
            self.rot_isr(True)

    def rot_isr(self, first):
        global display_item 
        global item_length

        if first:
            display_item += 1
        else:
            display_item -= 1

        if display_item < 0:
            display_item = item_length - 1

        if display_item >= item_length:
            display_item = 0
       
        self.clk_int = False
        self.dt_int = False

def init():
    # change the i2c1 bus frequency to 1 MHz
    subprocess.call('sudo sh -c "echo 1000000 > /sys/bus/i2c/devices/i2c-1/bus_clk_rate"', shell=True)

    #  initiialise buses
    # I2C Buses
    i2c0_bus = busio.I2C(board.SCL_1, board.SDA_1, frequency=100000)
    i2c1_bus = busio.I2C(board.SCL, board.SDA, frequency=1000000)

    # GPS is connected to TX1 and RX1 on Jetson Nano
    port = '/dev/ttyTHS1'
    # initialise the serial port with a baudrate of 9600
    uart = serial.Serial(port, baudrate=9600, timeout=30)
    
    # initialise sensors
    air530 = GPS(uart, debug=False)
    
    bme680 = Adafruit_BME680_I2C(i2c0_bus, address=0x76)
    bme680.sea_level_pressure = 1013.25
   
    hm3301 = HM3301_I2C(i2c0_bus, address=0x40)

    rot_enc = rotary_encoder()

    oled1 = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c1_bus, addr=0x3c)
    oled1.fill(0)
    oled1.show()

    oled2 = SSD1306_I2C(OLED_WIDTH, OLED_HEIGHT, i2c1_bus, addr=0x3d)
    oled2.fill(0)
    oled2.show()

    return [air530, bme680, hm3301, rotary_encoder],  [oled1, oled2]

def get_air530_data(air530):

    latitude = None
    longitude = None
    altitude = None
    date_time = None

    #air530.update()

    if not air530.has_fix:
        retval = ['No Fix', 'No Fix'] 
    else:
        UTC_time = air530.timestamp_utc
        if UTC_time[0] != 0:
            UTC_datetime = datetime.fromtimestamp(mktime(UTC_time))
            retval_date = UTC_datetime.strftime('%d-%b-%Y\n%H-%M-%S')

            latitude = air530.latitude
            longitude = air530.longitude
            altitude = air530.altitude_m

            retval_loc = f'Lat: {latitude:.4f}\nLon: {longitude:.4f}'

            retval = [retval_date, retval_loc] 
        
        else:
            retval = ['No Fix', 'No Fix'] 

    return retval

def get_hm3301_data(hm3301):
    # acquire the data
    try:
        PM_std = hm3301.get_std_readings()
        retval = [f'PM1.0: {PM_std[0]}ug/m3\nPM2.5: {PM_std[1]}ug/m3\nPM10: {PM_std[2]}ug/m3']

    except:
        retval = ['Read\nError']

    return retval

def get_bme680_data(bme680):
    # acquire the data

    try:
        temp = bme680.temperature
        humd = bme680.relative_humidity
        pres = bme680.pressure
        #gas =  bme680.gas

        retval = [f'{temp:.1f}°C', f'{humd:.1f} %', f'{pres:.0f} hPa']

    except:
        retval = ['Read\nError', 'Read\nError', 'Read\nError']

    return retval


def display_data(oled, text, data=False):
    # create a blank image on which the text will be placed
    image = Image.new('1', (oled.width, oled.height))
    draw = ImageDraw.Draw(image)

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, oled.width, oled.height), outline=0, fill=0)

    # First define some constants to allow easy resizing of shapes.
    padding = -2
    top = padding
    bottom = oled.height-padding
    
    # parse the text
    items = text.split('\n')
  
    if data: 
        for i, item in enumerate(items):
            if len(items) == 1:
                w, h = draw.textsize(item, font_huge)
                draw.text(((oled.width-w)/2+2, top+15+(i*25)), item, font=font_huge, fill=255)
            elif len(items) == 2:
                w, h = draw.textsize(item, font_big)
                draw.text(((oled.width-w)/2+2, top+5+(i*23)), item, font=font_big, fill=255)
            else:
                w, h = draw.textsize(item, font_default)
                draw.text(((oled.width-w)/2+2, top+3+(i*20)), item, font=font_default, fill=255)
    else:
        for i, item in enumerate(items):
            w, h = draw.textsize(item, font_big)
            draw.text(((oled.width-w)/2+2, top+5+(i*23)), item, font=font_big, fill=255)

    
    # Display the image.
    oled.image(image)
    #oled.show()

################################################################################################################################

sensors, oleds = init()
data_names = ['UTC\n Date & Time', 'GPS\nCoordinates', 'Ambient\nTemperature', 'Ambient\nHumidity', 'Ambient\nAir Pressure', 'Ambient\nPM Values']

while True:
    
    current = time.monotonic()
    sensors[0].update()

    if current - last_acq >= read_interval:
        last_acq = current

        sensor_data = []

        sensor_data.extend(get_air530_data(sensors[0]))
        sensor_data.extend(get_bme680_data(sensors[1]))
        sensor_data.extend(get_hm3301_data(sensors[2]))

        item_length = len(sensor_data)
    
        #print(sensor_data)

    display_data(oleds[0], data_names[display_item], data=False)
    display_data(oleds[1], sensor_data[display_item], data=True)
    
    oleds[0].show()
    oleds[1].show()


