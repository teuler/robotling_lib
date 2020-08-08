# ----------------------------------------------------------------------------
# teraranger_evomini.py
# Class for TeraRanger Evo Mini 4-pixel distance sensor
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-08-08, v1
#
# ----------------------------------------------------------------------------
import select
import array
from machine import UART
from micropython import const
from misc.helpers import timed_function

try:
  import struct
except ImportError:
  import ustruct as struct

__version__ = "0.1.0.0"
CHIP_NAME   = "tera_evomini"
CHAN_COUNT  = const(4)

# pylint: disable=bad-whitespace
# User facing constants/module globals.
TERA_DIST_NEG_INF   = const(0x0000)
TERA_DIST_POS_INF   = const(0xFFFF)
TERA_DIST_INVALID   = const(0x0001)
TERA_POLL_WAIT_MS   = const(10)

# pylint: disable=bad-whitespace
# Internal constants and register values:
_TERA_BAUD          = 115200
_TERA_CMD_WAIT_MS   = const(25)
_TERA_START_CHR     = const(0x54)
_TERA_OUT_MODE_TEXT = bytearray([0x00, 0x11, 0x01, 0x45])
_TERA_OUT_MODE_BIN  = bytearray([0x00, 0x11, 0x02, 0x4C])
_TERA_PIX_MODE_1    = bytearray([0x00, 0x21, 0x01, 0xBC])
_TERA_PIX_MODE_2    = bytearray([0x00, 0x21, 0x03, 0xB2])
_TERA_PIX_MODE_4    = bytearray([0x00, 0x21, 0x02, 0xB5])
_TERA_RANGE_SHORT   = bytearray([0x00, 0x61, 0x01, 0xE7])
_TERA_RANGE_LONG    = bytearray([0x00, 0x61, 0x03, 0xE9])
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class TeraRangerEvoMini:
  """Driver for the TeraRanger Evo Mini 4-pixel distance sensor."""

  def __init__(self, _ch, _tx, _rx, _nPix=4, _short=True):
    """ Requires pins and channel for unused UART
    """
    self._uart = UART(_ch, _TERA_BAUD, tx=_tx, rx=_rx)
    self._nPix = _nPix
    self._short = _short

    # Set pixel mode and prepare buffer
    if self._nPix == 4:
      uart.write(_TERA_PIX_MODE_4)
    elif self._nPix == 2:
      uart.write(_TERA_PIX_MODE_2)
    else:
      self._nPix = 1
      uart.write(_TERA_PIX_MODE_1)
    sleep_ms(_TERA_CMD_WAIT_MS)
    self._nBufExp = _nPix*2 +2
    self._dist = array.array("i", [0]*self._nPix)

    # Set binary mode for results
    uart.write(TERA_OUT_MODE_BIN)
    sleep_ms(_TERA_CMD_WAIT_MS)

    # Set distance mode
    if self._short:
      uart.write(TERA_RANGE_SHORT)
    else:
      uart.write(TERA_RANGE_LONG)
    sleep_ms(_TERA_CMD_WAIT_MS)

    # Prepare polling construct
    self._poll = select.poll()
    self._poll.register(self._uart, select.POLLIN)

    self._isReady = True
    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(CHIP_NAME, "TeraRanger Evo Mini", __version__,
                  "ok" if self._isReady else "NOT FOUND"))

  def __deinit__(self):
    if self._uart is not None:
      self._uart.deinit()
      self._isReady == False

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _update(self):
    """ Update distance reading(s)
    """
    if self._uart is not None:
      # UART seems to be ready ...
      np = self_nPix
      self.poll.poll(TERA_POLL_WAIT_MS)
      buf = self._uart.readline()
      if buf and len(buf) == self.nBufExp and buf[0] == _TERA_START_CHR:
        # Is valid buffer
        if np == 4:
          self._dist = struct.unpack_from('>HHHH', buf[1:9])
        elif np == 2:
          self._dist = struct.unpack_from('>HH', buf[1:5])
        else:
          self._dist = struct.unpack_from('>H', buf[1:3])

  @property
  def distance(self):
    return self._dist

# ----------------------------------------------------------------------------
