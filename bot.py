DEBUG = False

import threading, time
from lib import mpu, thrust, cam, web, calc, claw, depth

MPU     = mpu.MPU(          DEBUG, 250, 2, 0.98                     )
DEPTH   = depth.DEPTH(      DEBUG                                   )
CALC    = calc.CALC(        DEBUG                                   )
THRUST  = thrust.THRUST(    DEBUG, [ 5, 6, 7, 8, 9, 10, 11, 12 ]    )
CLAW    = claw.CLAW(        DEBUG, 13                               )
WEB     = web.WEB(          DEBUG, "0.0.0.0", 5001                  )
CAM1    = cam.CAM(          DEBUG, "0.0.0.0", 5002, 0               )
CAM2    = cam.CAM(          DEBUG, "0.0.0.0", 5003, 4               )
CALC    = calc.CALC(        DEBUG                                   )

MPU.calibrateGyro(100)
threading.Thread(target=CAM1.run, daemon=True).start()
threading.Thread(target=CAM2.run, daemon=True).start()
threading.Thread(target=WEB.run, daemon=True).start()

while True:
    if not DEBUG:
        WEB.setDepthValues(DEPTH.getVals())
        for i,s in enumerate(CALC.calcMotorVals(MPU.compFilter(), WEB.getControllerValues())):
            THRUST.setOutput(i, s)
        CLAW.setValue(CALC.calcClawVals(WEB.getControllerValues()))

# all motor (+) points IN to vertical front-back square
#           5 ----- 6
#          /|      /|
#        1 -|---- 2 |
#        |  |     | |
#        |  7 ----| 8
#        | /      |/
#        3 ------ 4
