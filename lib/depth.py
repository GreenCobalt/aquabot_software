import time

class DEPTH:
    def __init__(self, DEBUG):
        self.DEBUG = DEBUG
        self.sensorVals = {
            "pressure": 0, # mbar
            "temperature": 0, # c
            "depth": 0,
        }

        if not DEBUG:
            import ms5837
            
            print("(D) Initializing Depth Sensor")
            self.sensor = ms5837.MS5837_30BA(0)
            if not sensor.init():
                print("Sensor could not be initialized")
            self.sensor.setFluidDensity(1000)
            print("(D) Done")

    def run():
        while True:
            if self.sensor.read():
                self.sensorVals = {
                    "pressure": self.sensor.pressure(), # mbar
                    "temperature": self.sensor.temperature(), # c
                    "depth": self.sensor.depth(),
                }
            time.sleep(0.1)

    def getVals():
        return self.sensorVals
        