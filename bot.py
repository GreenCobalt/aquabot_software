DEBUG = False

if not DEBUG:
    import smbus, pigpio
    pi = pigpio.pi()

import math, time
import numpy as np
from flask import Flask

class MPU:
    def __init__(self, gyro, acc, tau):
        self.gx = None; self.gy = None; self.gz = None
        self.ax = None; self.ay = None; self.az = None

        self.gyroXcal = 0
        self.gyroYcal = 0
        self.gyroZcal = 0

        self.gyroRoll = 0
        self.gyroPitch = 0
        self.gyroYaw = 0

        self.roll = 0
        self.pitch = 0
        self.yaw = 0

        self.dtTimer = 0
        self.tau = tau

        self.gyroScaleFactor, self.gyroHex = self.gyroSensitivity(gyro)
        self.accScaleFactor, self.accHex = self.accelerometerSensitivity(acc)

        self.bus = smbus.SMBus(0)
        self.address = 0x68

        self.bus.write_byte_data(self.address, 0x6B, 0x00)
        self.bus.write_byte_data(self.address, 0x1C, self.accHex)
        self.bus.write_byte_data(self.address, 0x1B, self.gyroHex)

    def gyroSensitivity(self, x):
        # Create dictionary with standard value of 500 deg/s
        return {
            250:  [131.0, 0x00],
            500:  [65.5,  0x08],
            1000: [32.8,  0x10],
            2000: [16.4,  0x18]
        }.get(x,  [65.5,  0x08])

    def accelerometerSensitivity(self, x):
        # Create dictionary with standard value of 4 g
        return {
            2:  [16384.0, 0x00],
            4:  [8192.0,  0x08],
            8:  [4096.0,  0x10],
            16: [2048.0,  0x18]
        }.get(x,[8192.0,  0x08])

    def eightBit2sixteenBit(self, reg):
        # Reads high and low 8 bit values and shifts them into 16 bit
        h = self.bus.read_byte_data(self.address, reg)
        l = self.bus.read_byte_data(self.address, reg+1)
        val = (h << 8) + l

        # Make 16 bit unsigned value to signed value (0 to 65535) to (-32768 to +32767)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def getRawData(self):
        self.gx = self.eightBit2sixteenBit(0x43)
        self.gy = self.eightBit2sixteenBit(0x45)
        self.gz = self.eightBit2sixteenBit(0x47)

        self.ax = self.eightBit2sixteenBit(0x3B)
        self.ay = self.eightBit2sixteenBit(0x3D)
        self.az = self.eightBit2sixteenBit(0x3F)

    def calibrateGyro(self, N):
        print("Calibrating gyro with " + str(N) + " points. Do not move!")

        for ii in range(N):
            self.getRawData()
            self.gyroXcal += self.gx
            self.gyroYcal += self.gy
            self.gyroZcal += self.gz
        self.gyroXcal /= N
        self.gyroYcal /= N
        self.gyroZcal /= N

        self.dtTimer = time.time()

    def processIMUvalues(self):
        # Update the raw data
        self.getRawData()

        # Subtract the offset calibration values
        self.gx -= self.gyroXcal
        self.gy -= self.gyroYcal
        self.gz -= self.gyroZcal

        # Convert to instantaneous degrees per second
        self.gx /= self.gyroScaleFactor
        self.gy /= self.gyroScaleFactor
        self.gz /= self.gyroScaleFactor

        # Convert to g force
        self.ax /= self.accScaleFactor
        self.ay /= self.accScaleFactor
        self.az /= self.accScaleFactor

    def compFilter(self):
        # Get the processed values from IMU
        self.processIMUvalues()

        # Get delta time and record time for next call
        dt = time.time() - self.dtTimer
        self.dtTimer = time.time()

        # Acceleration vector angle
        accPitch = math.degrees(math.atan2(self.ay, self.az))
        accRoll = math.degrees(math.atan2(self.ax, self.az))

        # Gyro integration angle
        self.gyroRoll -= self.gy * dt
        self.gyroPitch += self.gx * dt
        self.gyroYaw += self.gz * dt
        self.yaw = self.gyroYaw

        # Comp filter
        self.roll = (self.tau)*(self.roll - self.gy*dt) + (1-self.tau)*(accRoll)
        self.pitch = (self.tau)*(self.pitch + self.gx*dt) + (1-self.tau)*(accPitch)

        return np.array([self.roll, self.pitch, self.yaw])
           
class THRUST:
    def __init__(self, pins=[5,6,7,8,9,10,11,12]):
        print("Initializing motors on pins 5-12")
        self.angleTolerance = 5
        self.correctionAgressiveness = 100

        for pin in pins:
            pi.set_mode(pin, pigpio.OUTPUT)
            pi.set_servo_pulsewidth(pin, 1500)

    def setOutput(self, pin, speed):
        pi.set_servo_pulsewidth(pin, speed)

    def calcAngleCorrection(self, angle, desiredAngle):
        if (abs(desiredAngle - angle) > self.angleTolerance):
            return self.translate(desiredAngle - angle, -180, 180, -1, 1)
        else:
            return 0
        
    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin
        valueScaled = float(value - leftMin) / float(leftSpan)
        return rightMin + (valueScaled * rightSpan)

        
class CLAW:
    def __init__(self, pin=13):
        print("Initializing claw on pin 13")
        pi.set_mode(pin, pigpio.OUTPUT)
        pi.set_servo_pulsewidth(pin, 1500)
        
app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello world'
    
def calc(x):
    abx = abs(x)
    xsn = x / abx if not x == 0 else 1
    return xsn * ((-50 * math.cos(2*math.pi*abx) + 50) if (0 <= abx and abx <= 0.5) else 100)

if __name__ == '__main__':
    # 250, 500, 1000, 2000 [deg/s]
    # 2, 4, 7, 16 [g]
    if not DEBUG:
        mpu = MPU(250, 2, 0.98)
        mpu.calibrateGyro(100)
        motors = THRUST()
        claw = CLAW()
    app.run(debug=True, host='0.0.0.0')

    moveMode = False #True = stabilized
    dVel = np.array([0, 0, 0])
    dRot = np.array([0, 0, 0])
    dClaw = 0

    INC = 0
    while True:
        if not DEBUG:
            cRot = mpu.compFilter()
        else:
            cRot = np.array([0, 0, 0])

        if moveMode:
            #stab mode, do not set dRot = cRot, that will be handled physically by motors, DO SET dRot[2] = cRot[2], that is turning, and cannot be stabilized
            dRot[2] = cRot[2]
        else:
            #free mode, set dRot = cRot
            dRot = np.copy(cRot)

        #controller input here, measure joysticks, buttons, etc
        #desired angle 30 degrees more than is (in effect, speed of motors)
        #eg: 
        dRot[0] = cRot[0] + 10
        dVel[0] = 1

        #then take diff between dRot and cRot and set motors accordingly to move towards that angle
        mRot = dRot - cRot
        mVel = dVel

        #calculate motor values for movement based on mRot and mVel
        #apply to motors, claw
        mVals = np.array([1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500])
        for i,v in enumerate(mVals):
            #roll adjustment
            mVals[i] += 400*math.sin((math.pi/360)*mRot[0]) * (1 if i in [1,3,4,6] else -1)
            mVals[i] += 400*math.sin((math.pi/360)*mRot[1]) * (1 if i in [0,1,4,5] else -1)
            mVals[i] += 400*math.sin((math.pi/360)*mRot[2]) * (1 if i in [0,1,6,7] else -1)

            mVals[i] += 400*math.sin((math.pi/360)*mVel[0]) * (1 if i in [1,3,5,7] else -1)


        print(mVals)
        
# all motor (+) points IN to vertical front-back square
#   0-----------2
#       1-----------3
#                   
#                   
#   4-----------6
#       5-----------7