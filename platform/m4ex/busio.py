# ----------------------------------------------------------------------------
# busio.py
#
# Basic bus support
# (for CircuitPython, M4 express)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-12-09, v1
# 2020-08-09, v1.1 - `UART` is inherited from `busio`
# ----------------------------------------------------------------------------
from micropython import const
from busio import SPI, I2C
from busio import UART as _UART

__version__ = "0.1.1.0"

# ----------------------------------------------------------------------------
class SPIBus(object):
  """SPI bus access."""

  def __init__(self, freq, sc, mo, mi):
    self._spi = SPI(sc, mo, mi)
    if not self._spi.try_lock():
      print("ERROR: busio.SPIBus: no lock for configure()")
    else:
      try:
        self._spi.configure(baudrate=freq)
      finally:
        self._spi.unlock()

  @property
  def bus(self):
    return self._spi

  def write_readinto(self, wbuf, rbuf):
    if self._spi.try_lock():
      try:
        self._spi.write_readinto(wbuf, rbuf)
      finally:
        self._spi.unlock()

# ----------------------------------------------------------------------------
class I2CBus(object):
  """I2C bus access."""

  def __init__(self, _freq, _scl, _sda, code=0):
    self._i2cDevList = []
    if not code == 0:
      # Default to software implementation of I2C
      from bitbangio import I2C as softI2C
      self._i2c = softI2C(scl=_scl, sda=_sda, frequency=_freq)
      codeStr = "Software"
    else:
      # Hardware implementation ...
      self._i2c = I2C(scl=_scl, sda=_sda, frequency=_freq)
      codeStr = "Hardware"
    if not self._i2c.try_lock():
      print("ERROR: busio.I2CBus: no lock for scan()")
    else:
      try:
        print("{0} I2C bus frequency is {1} kHz".format(codeStr, _freq/1000))
        print("Scanning I2C bus ...")
        self._i2cDevList = self._i2c.scan()
        print("... {0} device(s) found ({1})"
              .format(len(self._i2cDevList), self._i2cDevList))
      finally:
        self._i2c.unlock()

  def deinit(self):
    self._i2c.deinit()

  @property
  def bus(self):
    return self._i2c

  @property
  def deviceAddrList(self):
    return self._i2cDevList

  def writeto(self, addr, buf, stop_=True):
    if self._i2c.try_lock():
      try:
        self._i2c.writeto(addr, buf, stop=stop_)
      finally:
        self._i2c.unlock()

  def readfrom_into(self, addr, buf):
    if self._i2c.try_lock():
      try:
        self._i2c.readfrom_into(addr, buf)
      finally:
        self._i2c.unlock()

# ----------------------------------------------------------------------------
class UART(object):
  """UART."""

  def __init__(self, id=1, baudrate=9600, bits=8, parity=None, stop=1, tx=None,
               rx=None, rxbuf=64, timeout=0):
    tout_s = timeout/1000
    self._uart = _UART(tx=tx, rx=rx, baudrate=baudrate, bits=bits,
                       parity=parity, stop=stop, timeout=tout_s,
                       receiver_buffer_size=rxbuf)

  def readline(self):
    return self._uart.readline()

  def write(self, buf):
    return self._uart.write(buf)

  def any(self):
    return self._uart.in_waiting()

  def deinit(self):
    if self._uart is not None:
      self._uart.deinit()

# ----------------------------------------------------------------------------
