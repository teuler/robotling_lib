# ----------------------------------------------------------------------------
# robotling_board.py
# Global definitions for robotling board.
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-13, v1
# 2018-12-22, v1.1 - pins for M4 feather express added
# 2020-01-01, v1.2 - pins for hexapod robotling added
# 2020-08-08, v1.3 - pin/device assignments into separate files
# ----------------------------------------------------------------------------
from micropython import const
from robotling_board_version import BOARD_VER
from robotling_lib.platform.platform import platform

__version__ = "0.1.3.0"

SPI_FRQ   = const(4000000)
I2C_FRQ   = const(400000)

# I2C devices, maximal clock frequencies:
# AMG88XX (Infrared Array Sensor “Grid-EYE”)  <= 400 KHz
# VL6180X (Time of Flight distance sensor)    <= 400 KHz
# CMPS12  (Compass)                           <= 400 KHz
# LSM303  (Compass)                           100, 400 KHz
# LSM9DS0 (Compass)                           100, 400 KHz

# ----------------------------------------------------------------------------
# Robotling/Hexapod board connections/pins
#
print("BOARD_VER")
if platform.ID == platform.ENV_ESP32_UPY:
  print(platform.ID)

  if BOARD_VER == 100:
    from robotling_lib.platform.board_robotling_1_0_huzzah32 import *
  elif BOARD_VER >= 110 and BOARD_VER < 200:
    from robotling_lib.platform.board_robotling_1_3_huzzah32 import *
  elif BOARD_VER == 200:
    from robotling_lib.platform.board_robotling_2_0_huzzah32 import *
  else:
    print("HERE")
    from robotling_lib.platform.board_none_huzzah32 import *

elif platform.ID == platform.ENV_ESP32_TINYPICO:
  from robotling_lib.platform.board_hexapod_0_3_tinypico import *

elif platform.ID == platform.ENV_CPY_SAM51:
  from robotling_lib.platform.board_robotling_1_3_sam51 import *

else:
  assert False, "No matching board found"

# ----------------------------------------------------------------------------
# The battery is connected to the pin via a voltage divider (1/2), and thus
# an effective voltage range of up to 7.8V (ATTN_11DB, 3.9V); the resolution
# is 12 bit (WITDH_12BIT, 4096):
# V = adc /4096 *2 *3.9 *0.901919 = 0.001717522
# (x2 because of voltage divider, x3.9 for selected range (ADC.ATTN_11DB)
#  and x0.901919 as measured correction factor)
BAT_N_PER_V   = 0.001717522

# ----------------------------------------------------------------------------
# Error codes
#
RBL_OK                      = const(0)
RBL_ERR_DEVICE_NOT_READY    = const(-1)
RBL_ERR_SPI                 = const(-2)
# ...

# ----------------------------------------------------------------------------
