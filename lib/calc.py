import numpy as np

class CALC():
    def __init__(self, DEBUG):
        self.DEBUG = DEBUG
        self.moveMode = True #True = stabilized
        self.motorDeadZone = 10

    def setMoveMove(self, value):
        self.moveMode = value

    def clamp(self, n, smallest, largest): 
        return max(smallest, min(n, largest))

    def fuseInput(self, motorID, vel, rot, maxVelVal, maxRotVal):
        output = 1500
        
        output += (vel[0] if (motorID in [1, 3, 5, 7]) else -1 * vel[0]) * (400 / maxVelVal)
        output += (vel[1] if (motorID in [4, 5, 6, 7]) else -1 * vel[1]) * (400 / maxVelVal)
        output += (vel[2] if (motorID in [2, 3, 6, 7]) else -1 * vel[2]) * (400 / maxVelVal)

        output += (rot[0] if (motorID in [2, 3, 4, 5]) else -1 * rot[0]) * (400 / maxRotVal)
        output += (rot[1] if (motorID in [0, 3, 4, 7]) else -1 * rot[1]) * (400 / maxRotVal)
        output += (rot[2] if (motorID in [0, 2, 5, 7]) else -1 * rot[2]) * (400 / maxRotVal)

        if ((output > 1500 + self.motorDeadZone) or (output < 1500 - self.motorDeadZone)):
            return self.clamp(output, 1100, 1900)
        else:
            return 1500
        
    def calcClawVals(self, controllerValues):
        return 1500 - (400 if controllerValues["button_trigger_l"] else 0) + (400 if controllerValues["button_trigger_r"] else 0)

    def calcMotorVals(self, mpuCompFilter, controllerValues):
        desiredVel = np.array([0, 0, 0])
        desiredRot = np.array([0, 0, 0])

        if not self.DEBUG:
            currentRot = mpuCompFilter
        else:
            currentRot = np.array([0, 0, 0])

        if self.moveMode:
            #stab mode, keep x and y stable by creating diff in dRot, do not set dRot = cRot, DO SET dRot[2] = cRot[2], that is turning, and cannot be stabilized
            desiredRot[2] = currentRot[2]
        else:
            #free mode, set dRot to be = cRot so no correction takes place
            desiredRot = np.copy(currentRot)

        # add controller input
        # (0, 1, 2) => (x, y, z) -> x = look up/down, y = rotate about tube axis, z = rotate compass-like
        desiredRot[0] += (controllerValues["axes"]["axis_l"][0] - 128) * (180 / 128)
        desiredRot[1] += (controllerValues["axes"]["axis_l"][1] - 128) * (180 / 128)
        desiredRot[2] += 0
        actionRot = desiredRot - currentRot

        # (0, 1, 2) => (x, y, z) -> x = left/right, y = forward/back, z = rotate compass-like
        desiredVel[0] += (controllerValues["axes"]["axis_r"][0] - 128) * (180 / 128)
        desiredVel[1] += (controllerValues["axes"]["axis_r"][1] - 128) * (180 / 128)
        desiredVel[2] += 0
        actionVel = desiredVel
        
        return [self.fuseInput(i, actionVel, actionRot, 180, 180) for i in range(8)]
