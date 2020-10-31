# ----------------------------------------------------------------------------
# aio.py
#
# Basic analog pin support
# (for CircuitPython)
#
# The MIT License (MIT)
# Copyright (c) 2018-2020 Thomas Euler
# 2018-12-09, v1
# 2020-10-31, v1.1, generally CircuitPython
# ----------------------------------------------------------------------------
from micropython import const
from analogio import AnalogIn as AnalogIn_

__version__ = "0.1.1.0"

MAX_ADC     = const(65535)

# ----------------------------------------------------------------------------
class AnalogIn(object):
  """Basic analog input."""

  def __init__(self, pin):
    self._pin = AnalogIn_(pin)

  def deinit(self):
    self._pin.deinit()

  @property
  def value(self):
    return self._pin.value

  @property
  def max_adc(self):
    return MAX_ADC

  @property
  def reference_voltage(self):
    return self._pin.reference_voltage

# ----------------------------------------------------------------------------
