import RPi.GPIO as GPIO

# pin definitions
sw_pin = 'GPIO_PE6'
dt_pin = 'GPIO_PZ0'
clk_pin = 'CAM_AF_EN'

class rotary_encoder:

    def __init__(self, sw_pin=sw_pin, dt_pin=dt_pin, clk_pin=clk_pin):
        # pin setup
        GPIO.setmode(GPIO.TEGRA_SOC)  # TEGRA_SOC pin-numbering scheme
        GPIO.setup([sw_pin, dt_pin, clk_pin], GPIO.IN)  #rotary encoder pins set as inputs

        # Interupts setup
        GPIO.add_event_detect(sw_pin, GPIO.FALLING, callback=self.sw_isr, bouncetime=200)
        GPIO.add_event_detect(clk_pin, GPIO.FALLING, callback=self.clk_isr, bouncetime=20)
        GPIO.add_event_detect(dt_pin, GPIO.FALLING, callback=self.dt_isr, bouncetime=20)

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
        self.clk_int = False
        self.dt_int = False

        if first:
            print("Turned Counter Clockwise")
        else:
            print('Turned Clockwise')
       


def main():

    rot = rotary_encoder()

    print("Starting demo now! Press CTRL+C to exit")
    try:
        while True:
            # do nothing
            pass
    finally:
        GPIO.cleanup()  # cleanup all GPIOs

if __name__ == '__main__':
    main()

