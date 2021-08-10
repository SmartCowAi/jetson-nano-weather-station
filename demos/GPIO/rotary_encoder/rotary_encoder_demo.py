import RPi.GPIO as GPIO

# pin definitions
sw_pin = 33
dt_pin = 31
clk_pin = 29

clk_int = False
dt_int = False

def sw_isr(channel):
    print("Switch Pressed")
    
def clk_isr(channel):
    global clk_int
    global dt_int
    
    clk_int = True
    
    if dt_int:
        rot_isr(first='dt')
    
def dt_isr(channel):
    global clk_int
    global dt_int
    
    dt_int = True
    
    if clk_int:
        rot_isr(first='clk')

def rot_isr(first):
    
    global clk_int
    global dt_int
    
    if first=='clk':
        print("Turned Counter Clockwise")
    else:
        print('Turned Clockwise')
       
    clk_int = False
    dt_int = False
        

def main():
    # pin setup
    GPIO.setmode(GPIO.BOARD)  # BOARD pin-numbering scheme
    GPIO.setup([sw_pin, dt_pin, clk_pin], GPIO.IN)  #rotary encoder pins set as inputs

    # Interupts setup
    GPIO.add_event_detect(sw_pin, GPIO.FALLING, callback=sw_isr, bouncetime=200)
    GPIO.add_event_detect(clk_pin, GPIO.FALLING, callback=clk_isr, bouncetime=100)
    GPIO.add_event_detect(dt_pin, GPIO.FALLING, callback=dt_isr, bouncetime=100)
    
    print("Starting demo now! Press CTRL+C to exit")
    try:
        while True:
            # do nothing
            pass
    finally:
        GPIO.cleanup()  # cleanup all GPIOs

if __name__ == '__main__':
    main()

