import serial
import pynmea2

import os

# GPS is connected to TX1 and RX1 on Jetson Nano
port = '/dev/ttyTHS1'

# initialise the serial port with a baudrate of 9600
ser = serial.Serial(port, baudrate=9600, timeout=1)

# initialse a dictionary to store the NMEA messages
nmea_messages = {}


def check_antenna_connected(nmea_TXT):
    if nmea_TXT.text == 'ANTENNA OK':
        return True

    return False

def get_coordinates(nmea_GGA):
    #returns the latitude, longitude and altitude as obtained from the GPS module
    
    return nmea_GGA.latitude, nmea_GGA.longitude, nmea_GGA.altitude

def get_datetime(nmea_ZDA):
    # retruns the date and time as obtained from the GPS module
    
    return nmea_ZDA.datetime


def process_messages(nmea_messages):
    
    if check_antenna_connected(nmea_messages['TXT']):
        print('Antenna Connected')
    else:
        print('Check Antenna Connection')
        
    print()
        
    if nmea_messages['GGA'].lat != '':
        
        lat_lon = get_coordinates(nmea_messages['GGA'])
        
        print('Latitude  = %.4f' %lat_lon[0])
        print('Longitude = %.4f' %lat_lon[1])
        print('Altitude  = %.2f m' %lat_lon[2])

    else:

        print('Cannot get GPS coordinates')
        print('Move the antenna closer to a window or outdoors')
        
    if nmea_messages['ZDA'].datetime != '':

        date_time = get_datetime(nmea_messages['ZDA'])
        print('UTC Date & Time = ', date_time)

    else:
        print('Cannot get Date & Time')

    print()
    

print('Seeed Air530 GPS Module Demo')
print('Press CTRL+C to exit')
print()

while True:
    try:
        # read the received data line by line
        data = ser.readline()

        # decode it into a string
        data = data.decode('utf-8')
    
        # the GPS module transmits a number of NMEA messages
        # each block of messages can be appended to a dictionart for easier processing
        
        # the last message is always the TXT one
        
        # parse the message 
        msg = pynmea2.parse(data)
        
        # append to the dictionary
        nmea_messages[type(msg).__name__] = msg
        
        # if it is the last message
        if type(msg).__name__ == 'TXT':
            # process message list
            process_messages(nmea_messages)

            # reset the dictionary
            nmea_messages = {}


    # exception handling
    except pynmea2.nmea.ParseError:
        pass

    except UnicodeDecodeError:
        pass

    except KeyboardInterrupt:
        # close serial port
        ser.close()

        print('Demo stopped')
        break

