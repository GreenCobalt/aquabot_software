class CLAW:
    def __init__(self, DEBUG, pin=13):
        self.DEBUG = DEBUG
        if not DEBUG:
            import pigpio
            print("(C) Initializing claw on pin 13")
            self.pi = pigpio.pi()
            pi.set_mode(pin, pigpio.OUTPUT)
            pi.set_servo_pulsewidth(pin, 1500)

    def setValue(self, value):
        if not self.DEBUG:
            self.pi.set_servo_pulsewidth(13, value)
