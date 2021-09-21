# ----------------------------------------------------------------------------
# lux_veml7700.py
# VEML7700 high precision I2C ambient light sensor
#
# The MIT License (MIT)
# Copyright (c) 2021 Thomas Euler
# 2021-07-12, v1
#
# Based on `adafruit_veml7700`
# https://github.com/adafruit/Adafruit_CircuitPython_VEML7700
# The MIT License (MIT)
#
# Copyright (c) 2019 Kattni Rembor for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
# ----------------------------------------------------------------------------
from micropython import const
import robotling_lib.misc.ansi_color as ansi
from robotling_lib.sensors.sensor_base import SensorBase

from robotling_lib.platform.platform import platform as pf
if pf.languageID == pf.LNG_CIRCUITPYTHON:
  from robotling_lib.platform.circuitpython.register.i2c_struct \
    import UnaryStruct, ROUnaryStruct
  from robotling_lib.platform.circuitpython.register.i2c_bits import RWBits
  from robotling_lib.platform.circuitpython.register.i2c_bit import RWBit, ROBit
  from robotling_lib.platform.circuitpython.bus_device.i2c_device \
    import I2CDevice
else:
  print(ansi.RED +"ERROR: No matching libraries in `platform`." +ansi.BLACK)

# pylint: disable=bad-whitespace
__version__ = "0.1.0.0"
CHIP_NAME   = "VEML7700"
CHAN_COUNT  = const(1)
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class VEML7700(SensorBase):
  """Driver for the VEML7700 ambient light sensor."""

  # pylint: disable=bad-whitespace
  # Ambient light sensor gain settings
  ALS_GAIN_1   = const(0x0)
  ALS_GAIN_2   = const(0x1)
  ALS_GAIN_1_8 = const(0x2)
  ALS_GAIN_1_4 = const(0x3)

  # Ambient light integration time settings
  ALS_25MS     = const(0xC)
  ALS_50MS     = const(0x8)
  ALS_100MS    = const(0x0)
  ALS_200MS    = const(0x1)
  ALS_400MS    = const(0x2)
  ALS_800MS    = const(0x3)

  # Gain value integers
  gain_values = {
      ALS_GAIN_2:   2,
      ALS_GAIN_1:   1,
      ALS_GAIN_1_4: 0.25,
      ALS_GAIN_1_8: 0.125,
    }
  # Integration time value integers
  integration_time_values = {
      ALS_25MS:  25,
      ALS_50MS:  50,
      ALS_100MS: 100,
      ALS_200MS: 200,
      ALS_400MS: 400,
      ALS_800MS: 800,
    }
  # pylint: enable=bad-whitespace

  # ALS - Ambient light sensor high resolution output data
  light = ROUnaryStruct(0x04, "<H")

  # WHITE - White channel output data
  white = ROUnaryStruct(0x05, "<H")

  # ALS_CONF_0 - ALS gain, integration time, interrupt and shutdown.
  light_shutdown = RWBit(0x00, 0, register_width=2)
  """ Ambient light sensor shutdown. When ``True``, ambient light sensor is
     disabled.
  """
  light_interrupt = RWBit(0x00, 1, register_width=2)
  """ Enable interrupt. ``True`` to enable, ``False`` to disable.
  """
  light_gain = RWBits(2, 0x00, 11, register_width=2)
  """ Ambient light gain setting. Gain settings are 2, 1, 1/4 and 1/8.
      Settings options are:
        ALS_GAIN_2, ALS_GAIN_1, ALS_GAIN_1_4, ALS_GAIN_1_8.
  """
  light_integration_time = RWBits(4, 0x00, 6, register_width=2)
  """ Ambient light integration time setting. Longer time has higher
      sensitivity. Can be:
        ALS_25MS, ALS_50MS, ALS_100MS, ALS_200MS, ALS_400MS, ALS_800MS.
  """

  # ALS_WH - ALS high threshold window setting
  light_high_threshold = UnaryStruct(0x01, "<H")
  """ Ambient light sensor interrupt high threshold setting.
  """
  # ALS_WL - ALS low threshold window setting
  light_low_threshold = UnaryStruct(0x02, "<H")
  """ Ambient light sensor interrupt low threshold setting.
  """
  # ALS_INT - ALS INT trigger event
  light_interrupt_high = ROBit(0x06, 14, register_width=2)
  """ Ambient light high threshold interrupt flag. Triggered when high
      threshold exceeded.
  """
  light_interrupt_low = ROBit(0x06, 15, register_width=2)
  """ Ambient light low threshold interrupt flag. Triggered when low
      threshold exceeded.
  """

  def __init__(self, i2c, address=0x10):
    """ Requires already initialized I2C bus instance.
    """
    self._i2c_addr = address
    if pf.languageID == pf.LNG_CIRCUITPYTHON:
      self.i2c_device = I2CDevice(i2c._i2c, address)
    else:
      self.i2c_device = i2c
    self._isReady = False
    super().__init__(None, 0)
    for _ in range(3):
      try:
        # Enable the ambient light sensor
        self.light_shutdown = False
        self._isReady = True
        break
      except OSError:
        pass

    c = ansi.GREEN if self._isReady else ansi.RED
    cn = "{0}_v{1}".format(CHIP_NAME, self._version)
    print(c +"[{0:>12}] {1:35} ({2}): {3}"
          .format(cn, self._type, __version__,
                  "ok" if self._isReady else "FAILED") +ansi.BLACK)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def integration_time_value(self):
    """ Integration time value in integer form.
        Used for calculating :meth:`resolution`.
    """
    integration_time = self.light_integration_time
    return self.integration_time_values[integration_time]

  def gain_value(self):
    """ Gain value in integer form. Used for calculating :meth:`resolution`.
    """
    gain = self.light_gain
    return self.gain_values[gain]

  def resolution(self):
    """ Calculate the :meth:`resolution`` necessary to calculate lux. Based on
        integration time and gain settings.
    """
    resolution_at_max = 0.0036
    gain_max = 2
    integration_time_max = 800
    if (
        self.gain_value() == gain_max and
        self.integration_time_value() == integration_time_max
      ):
      return resolution_at_max
    return (
        resolution_at_max
        *(integration_time_max /self.integration_time_value())
        *(gain_max /self.gain_value())
      )

  @property
  def lux(self):
    """ Light value in lux.
    """
    return self.resolution() *self.light

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def is_ready(self):
    return self._isReady

  @property
  def channel_count(self):
    return CHAN_COUNT

# ----------------------------------------------------------------------------
