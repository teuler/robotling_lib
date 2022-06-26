# ----------------------------------------------------------------------------
# pololu_tof_ranging.py
# Pololu time-of-flight distance ranging sensors w/ PWM output
#
# The MIT License (MIT)
# Copyright (c) 2021-2022 Thomas Euler
# 2021-05-02, v1
# 2021-02-12, v1.1
# 2022-04-08, v1.2, improve sensor performance
# 2022-04-15, v1.3, back to simple `time_pulse_us`, PIO in a different file
# ----------------------------------------------------------------------------
from time import ticks_diff, ticks_us
from micropython import const
from machine import Pin, time_pulse_us
from robotling_lib.sensors.sensor_base import SensorBase
import robotling_lib.misc.ansi_color as ansi
from robotling_lib.misc.helpers import timed_function

# pylint: disable=bad-whitespace
__version__    = "0.1.3.0"
CHIP_NAME      = "IRS16A"
TIMEOUT_US     = const(20_000)
N_REREADS      = const(2)
N_AVG          = const(1)
ERR_TIMEOUT    = const(-1)
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class PololuTOFRangingSensor(SensorBase):
  """Class for pulse-width Pololu time-of-flight ranging sensor."""

  def __init__(self, pin):
    super().__init__(driver=None, chan=1)
    self._pin = Pin(pin)
    self._type = "time-of-flight range"
    self._isReady = self.range_cm is not ERR_TIMEOUT
    c = ansi.GREEN if self._isReady else ansi.RED
    print(c +"[{0:>12}] {1:35} ({2}): {3}"
          .format(CHIP_NAME, "Pololu time-of-flight", __version__,
                  "ok" if self._isReady else "NOT FOUND") +ansi.BLACK)
  
  def deinit(self):
    pass
      
  @property
  def range_raw(self):
    return time_pulse_us(self._pin, 1, TIMEOUT_US)

  @micropython.native
  @property
  def range_cm(self):
    tavg = 0              
    p = self._pin
    t = 0
    for i in range(N_AVG):
      n = N_REREADS
      while (t := time_pulse_us(p, 1, TIMEOUT_US)) < 1000 and n > 0:
        n -= 1
      if t < 0 or n == 0:
        return ERR_TIMEOUT
      tavg += t
    tavg /= N_AVG
    return 0.75 *(tavg -1000) /10
  
# ----------------------------------------------------------------------------
