# ----------------------------------------------------------------------------
# sharp_ir_ranging.py
# Analog Sharp IR range sensors
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-23, v1
# 2019-08-03, new type of Sharp sensor added (GP2Y0AF15X, 1.5-15 cm)
# 2019-12-21, native code generation added (requires MicroPython >=1.12)
# ----------------------------------------------------------------------------
import array
from math import exp
from robotling_lib.sensors.sensor_base import SensorBase

# pylint: disable=bad-whitespace
__version__    = "0.1.1.0"
CHIP_NAME_0    = "GP2Y0A41SK0F"  # 4 to 30 cm
CHIP_NAME_1    = "GP2Y0AF15X"    # 1.5 to 15 cm
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class SharpIRRangingSensor(SensorBase):
  """Base class for analog Sharp IR ranging sensors."""

  def __init__(self, driver, chan):
    super().__init__(driver, chan)
    self._type = "IR range"
    self._coef = array.array('f', [1,1,1,1])
    self._maxV = driver.max_value

  @property
  def range_raw(self):
    if self._autoUpdate:
      self._driver.update()
    return self._driver.data[self._chan]

  @micropython.native
  @property
  def range_cm(self):
    if self._autoUpdate:
      self._driver.update()
    cf = self._coef
    mx = self._maxV
    x = self._driver.data[self._chan]
    x = x if mx == 4095 else (x/mx)*4095
    return cf[0]+ cf[1]*exp(-cf[2]*x)+cf[3]*exp(-cf[4]*x)

# The following interface classes require an already initialised sensor driver
# instance and the channel assigned to this sensor instance.
# The range ('range_cm') is calibrated for the respective Sharp sensor model
#  using coefficients from a double exponential fit.
#
class GP2Y0A41SK0F(SharpIRRangingSensor):
  """Interface class for Sharp GP2Y0A41SK0F IR ranging sensors (4-30 cm)."""

  def __init__(self, driver, chan):
    super().__init__(driver, chan)
    self._type = "IR ranging (Sharp)"
    self._coef = array.array('f', [-1.995,12.9, 0.000329958, 93.928, 0.003793])
    tx = "{0}, A/D channel #{1}".format(self._type, chan)
    print("[{0:>12}] {1:35} ({2}): ok"
          .format(CHIP_NAME_0, tx, __version__))

class GP2Y0AF15X(SharpIRRangingSensor):
  """Interface class for Sharp GP2Y0AF15X IR ranging sensors (1.5-15 cm)."""

  def __init__(self, driver, chan):
    super().__init__(driver, chan)
    self._type = "IR ranging (Sharp)"
    self._coef = array.array('f', [1.3249, 20.436, 0.0021805, 24.613, 0.064151])
    tx = "{0}, A/D channel #{1}".format(self._type, chan)
    print("[{0:>12}] {1:35} ({2}): ok"
          .format(CHIP_NAME_1, tx, __version__))

# ----------------------------------------------------------------------------
