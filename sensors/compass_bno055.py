# ----------------------------------------------------------------------------
# compass_bno055.py
# Compass based on BNO055 9-DoF MNU driver
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2020-09-20, v1
# ----------------------------------------------------------------------------
#from math import radians
#from micropython import const
from robotling_lib.misc.helpers import timed_function
from robotling_lib.sensors.sensor_base import SensorBase
from robotling_lib.driver.bno055 import BNO055, _ADDRESS_BNO055

__version__ = "0.1.0.0"
CHIP_NAME   = "BNO055"

# pylint: disable=bad-whitespace
# ...
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class Compass(SensorBase):
  """Compass class that uses the 9-DoF MNU BNO055 breakout."""

  def __init__(self, i2c):
    """ Requires already initialized I2C bus instance.
    """
    self._i2c = i2c
    self._BNO055 = None
    self._isReady = False
    self._type = "Compass w/ tilt-compensation"
    self._heading = 0.0
    self._pitch = 0.0
    self._roll = 0.0
    super().__init__(None, 0)

    addrList = self._i2c.deviceAddrList
    if (_ADDRESS_BNO055 in addrList):
      # Initialize
      try:
        self._BNO055 = BNO055(i2c, _ADDRESS_BNO055)
        self._isReady = True
      except RuntimeError:
        pass

    cn =  "{0}_v{1}".format(CHIP_NAME, self._version)
    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(cn, self._type, __version__,
                  "ok" if self._isReady else "FAILED"))

****
  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  @micropython.native
  def getHeading(self, tilt=False, calib=False, hires=True):
    """ Returns heading with or w/o tilt compensation and/or calibration,
        if available.
        NOTE: The CMPS12 has built-in tilt compensation and is pre-calibra-
        ted, therefore the parameters "tilt" and "calib" are only for
        compatibility reasons and have no effect. With "hires"=True, the
        precision is 3599/360°, otherwise 255/360°.
    """
    if not self._isReady:
      return rb.RBL_ERR_DEVICE_NOT_READY
    hd = self._heading
    if hires:
      buf = bytearray(1)
      self._read_bytes(_ADDRESS_CMPS12, _REG_BEARING_8BIT, buf)
      hd  = buf[0]/255 *360
    else:
      buf = bytearray(2)
      self._read_bytes(_ADDRESS_CMPS12, _REG_BEARING_16BIT_HB, buf)
      hd  = ((buf[0] << 8) | buf[1]) /10
    return hd


  #@timed_function
  @micropython.native
  def getHeading3D(self, calib=False):
    """ Returns heading, pitch and roll in [°] with or w/o calibration,
        if available.
        NOTE: The CMPS12 has built-in tilt compensation and is pre-calibra-
        ted, therefore the parameter "calib" exists only for compatibility
        reasons and has no effect.
    """
    if not self._isReady:
      return (rb.RBL_ERR_DEVICE_NOT_READY, 0, 0, 0)
    hd  = self._heading
    pit = self._pitch
    rol = self._roll
    buf = bytearray(4)
    self._read_bytes(_ADDRESS_CMPS12, _REG_BEARING_16BIT_HB, buf)
    hd, pit, rol = struct.unpack_from('>Hbb', buf[0:4])
    hd /= 10
    return (rb.RBL_OK, hd, pit, rol)


  #@timed_function
  @micropython.native
  def getPitchRoll(self, radians=False):
    """ Returns error code, pitch and roll in [°] as a tuple
    """
    if not self._isReady:
      return  (rb.RBL_ERR_DEVICE_NOT_READY, 0, 0)
    pit = self._pitch
    rol = self._roll
    buf = bytearray(2)
    self._read_bytes(_ADDRESS_CMPS12, _REG_PITCH_8BIT_ANGLE, buf)
    pit, rol = struct.unpack_from('>bb', buf[0:2])
    if radians:
      return (rb.RBL_OK, -1, radians(pit), radians(rol))
    else:
      return (rb.RBL_OK, -1, pit, rol)


  @property
  def isReady(self):
    return self._isReady

  @property
  def channelCount(self):
    return CHAN_COUNT

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _read_bytes(self, i2cAddr, regAddr, buf):
    cmd    = bytearray(1)
    cmd[0] = regAddr & 0xff
    self._i2c.bus.writeto(i2cAddr, cmd, False)
    self._i2c.bus.readfrom_into(i2cAddr, buf)

# ----------------------------------------------------------------------------
