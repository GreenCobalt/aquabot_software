DEBUG = True

import threading, time
from lib import mpu, thrust, cam, web, calc, claw

MPU     = mpu.MPU(          DEBUG, 250, 2, 0.98                     )
CALC    = calc.CALC(        DEBUG                                   )
THRUST  = thrust.THRUST(    DEBUG, [ 5, 6, 7, 8, 9, 10, 11, 12 ]    )
CLAW    = claw.CLAW(        DEBUG, 13                               )
WEB     = web.WEB(          DEBUG, "0.0.0.0", 5001                  )
CAM     = cam.CAM(          DEBUG, "0.0.0.0", 5002, 0               )
CALC    = calc.CALC(        DEBUG                                   )

MPU.calibrateGyro(100)
threading.Thread(target=CAM.run, daemon=True).start()
threading.Thread(target=WEB.run, daemon=True).start()

while True:
    for i,s in enumerate(CALC.calcMotorVals(MPU.compFilter(), WEB.getControllerValues())):
        #print(i, s)
        if not DEBUG:
            THRUST.setOutput(i, s)

# all motor (+) points IN to vertical front-back square
#           5 ----- 6
#          /|      /|
#        1 -|---- 2 |
#        |  |     | |
#        |  7 ----| 8
#        | /      |/
#        3 ------ 4
