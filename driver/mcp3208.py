# ----------------------------------------------------------------------------
# mcp3208.py
# Class for 8-channel 12-bit SPI A/D converter MCP3208 driver
#
# The MIT License (MIT)
# Copyright (c) 2018-2022 Thomas Euler
# 2018-09-20, v1
# 2018-11-25, v1.1, now uses dio_*.py to access machine
# 2020-01-01, v1.2, micropython.native
# 2021-05-08, v1.2, property naming changed
# 2022-01-02, v1.3, rp2 added as option
# ----------------------------------------------------------------------------
import array
from micropython import const
from robotling_lib.misc.helpers import timed_function
import robotling_lib.misc.ansi_color as ansi

from robotling_lib.platform.platform import platform as pf
if pf.languageID == pf.LNG_MICROPYTHON:
  if pf.isRP2:
    import robotling_lib.platform.rp2.dio as dio
  else:    
    import robotling_lib.platform.esp32.dio as dio
elif pf.languageID == pf.LNG_CIRCUITPYTHON:
  import robotling_lib.platform.circuitpython.dio as dio
else:
  print(ansi.RED +"ERROR: No matching libraries in `platform`." +ansi.BLACK)

# pylint: disable=bad-whitespace
__version__     = "0.1.2.1"

CHIP_NAME       = "mcp3208"
CHAN_COUNT      = const(8)
MAX_VALUE       = const(4095)
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class MCP3208(object):
  """Driver for 8-channel 12-bit SPI A/D converter MCP3208."""

  def __init__(self, spi, pinCS):
    """ Requires already initialized SPIBus instance to access the 12-bit
        8 channel A/D converter IC (MCP3208). For performance reasons,
        not much validity checking is done.
    """
    self._spi = spi
    self._cmd = bytearray(b'\x00\x00\x00')
    self._buf = bytearray(3)
    self._data = array.array('i', [0]*CHAN_COUNT)
    self._pinCS = dio.DigitalOut(pinCS, value=True)
    self._channelMask = 0x00

    print(ansi.GREEN +"[{0:>12}] {1:35} ({2}): ok"
          .format(CHIP_NAME, "8-channel A/D", __version__) +ansi.BLACK)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  def read_adc(self, chan):
    """ Returns A/D value of channel `chan` or `-1`, if an error occurs
    """
    cm = self._cmd
    bf = self._buf
    wr = self._spi.write_readinto
    try:
      cm[0] = 0b11000000 +((chan & 0x07) << 3)
      self._pinCS.value = 0
      wr(cm, bf)
      self._pinCS.value = 1
      val = (((bf[0] & 1) << 11) | (bf[1] << 3) | (bf[2] >> 5)) & 0x0FFF
      return val
    except OSError as Err:
      print("{0}: {1}".format(self.__class__.__name__, Err))
    return -1

  @timed_function
  def update_timed(self):
    self.update()

  @micropython.native
  def update(self):
    """ Updates the A/D data for the channels indicated by the property
        `channelMask`. The data can then be accessed as an array via the
        property "data".
    """
    mk = self._channelMask
    if mk > 0:
      cm = self._cmd
      bf = self._buf
      da = self._data
      rg = range(CHAN_COUNT)
      wr = self._spi.write_readinto
      try:
        for i in rg:
          if mk & (0x01 << i):
            cm[0] = 0b11000000 +(i << 3)
            self._pinCS.value = 0
            wr(cm, bf)
            self._pinCS.value = 1
            da[i] = ((bf[0] & 1) << 11) | (bf[1] << 3) | (bf[2] >> 5) & 0x0FFF
      except OSError as Err:
        print("{0}: {1}".format(self.__class__.__name__, Err))

  @property
  def data(self):
    """ Array with A/D data
    """
    return self._data

  @property
  def channel_count(self):
    return CHAN_COUNT

  @property
  def max_value(self):
    return MAX_VALUE

  @property
  def channel_mask(self):
    return self._channelMask

  @channel_mask.setter
  def channel_mask(self, value):
    value &= 0xff
    self._channelMask = value

# ----------------------------------------------------------------------------
