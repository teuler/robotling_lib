# ----------------------------------------------------------------------------
# platform.py
# Class that determines board and MicroPython distribution
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-21, v1
# 2018-09-21, v1.1, language ID added
# 2020-12-12, v1.2, FeatherS2 added
# ----------------------------------------------------------------------------
from os import uname
from micropython import const

__version__ = "0.1.2.0"

# ----------------------------------------------------------------------------
class Platform(object):
  """Board type and MicroPython distribution."""

  ENV_UNKNOWN           = const(0)
  ENV_ESP32_UPY         = const(1)
  ENV_ESP32_TINYPICO    = const(2)
  ENV_CPY_FEATHERS2     = const(3)
  ENV_CPY_SAM51         = const(4)
  ENV_CPY_NRF52         = const(5)

  LNG_UNKNOWN           = const(0)
  LNG_MICROPYTHON       = const(1)
  LNG_CIRCUITPYTHON     = const(2)

  def __init__(self):
    # Determine distribution, board type and GUID
    self._distID    = ENV_UNKNOWN
    self.sysInfo    = uname()

    if self.sysInfo[0] == "esp32":
      if self.sysInfo[4].upper().find("TINYPICO") >= 0:
        self._envID = ENV_ESP32_TINYPICO
      else:
        self._envID = ENV_ESP32_UPY
    if self.sysInfo[0] == "samd51":
      self._envID = ENV_CPY_SAM51
    if self.sysInfo[0] == "nrf52":
      self._envID = ENV_CPY_NRF52
    if self.sysInfo[0] == "esp32s2":
      self._envID = ENV_CPY_FEATHERS2

    if self._envID in [ENV_ESP32_UPY, ENV_ESP32_TINYPICO]:
      self._lngID = LNG_MICROPYTHON
    elif self._envID in [ENV_CPY_SAM51, ENV_CPY_NRF52, ENV_CPY_FEATHERS2]:
      self._lngID = LNG_CIRCUITPYTHON
    else:
      self._lngID = LNG_UNKNOWN

    try:
      from machine import unique_id
      from binascii import hexlify
      self._boardGUID = b'robotling_' +hexlify(unique_id())
    except ImportError:
      self._boardGUID = b'robotling_n/a'

  @property
  def ID(self):
    return self._envID

  @ID.setter
  def ID(self, value):
    self._envID = value

  @property
  def GUID(self):
    return self._boardGUID

  @property
  def language(self):
    return ["MicroPython", "CircuitPython", "n/a"][self._lngID]

  @property
  def languageID(self):
    return self._lngID

# ----------------------------------------------------------------------------
platform = Platform()

# ----------------------------------------------------------------------------
