class THRUST:
    def __init__(self, DEBUG, pins=[5,6,7,8,9,10,11,12]):
        self.DEBUG = DEBUG
        self.pins = pins
        if not DEBUG:
            import pigpio
            self.pi = pigpio.pi()
    
            print("(T) Initializing motors on pins ", pins)
            for pin in pins:
                self.pi.set_mode(pin, pigpio.OUTPUT)
                self.pi.set_servo_pulsewidth(pin, 1500)
            print("(T) Done")

    def getPin(self, motorID):
        return self.pins[motorID]

    def setOutput(self, motor, speed):
        if not self.DEBUG:
            self.pi.set_servo_pulsewidth(self.getPin(motor), speed)
        else:
            print(motor, self.getPin(motor), speed)
