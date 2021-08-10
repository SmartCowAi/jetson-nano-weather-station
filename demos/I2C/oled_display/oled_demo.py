import time
import os

import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

# 128x32 display with hardware I2C:
disp = Adafruit_SSD1306.SSD1306_128_64(rst=None, i2c_bus=1, gpio=1)

# Initialize library.
disp.begin()

# Clear display.
disp.clear()
disp.display()

# Create blank image for drawing.
# Make sure to create image with mode '1' for 1-bit color.
width = disp.width
height = disp.height
image = Image.new('1', (width, height))

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0,0,width,height), outline=0, fill=0)

# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height-padding

# Set the font to Oswald-Medium
fwd = os.path.dirname(os.path.abspath(__file__))
font_default = ImageFont.truetype(fwd + '/fonts/Oswald-Medium.ttf', 16)
font_big = ImageFont.truetype(fwd + '/fonts/Oswald-Medium.ttf', 30)

text_list = ['SmartCow AI\nTechnologies\nOLED Demo','Temperature\n24.6°C', 'Humidity\n55%', 'Air Pressure\n1014 hPa', 'PM1.0: 12ug/m3\nPM2.5: 225ug/m3\nPM10: 129ug/m3', 'GPS Coordinates\nLat: 35.915\nLon: 14.495', 'Date & Time\n9-Jul-2021\n10:21:25']

print('Starting Demo')
print('Press CTRL+C to exit')

while True:
    
    for text in text_list:
        items = text.split('\n')

        for i, item in enumerate(items):
            if len(items) == 2 and i == 1:
                w, h = draw.textsize(item, font_big)
                draw.text(((width-w)/2, top+(i*20)), item, font=font_big, fill=255)
            else:    
                w, h = draw.textsize(item, font_default)
                draw.text(((width-w)/2, top+(i*20)), item, font=font_default, fill=255)

        
        # Display image.
        disp.image(image)
        disp.display()
        time.sleep(1.5)
        
        # clear the display
        draw.rectangle((0,0,width,height), outline=0, fill=0)
        

