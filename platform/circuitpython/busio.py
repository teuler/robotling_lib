# ----------------------------------------------------------------------------
# busio.py
#
# Basic bus support
# (for CircuitPython)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-12-09, v1
# 2020-08-09, v1.1, `UART` is inherited from `busio`
# 2020-10-09, v1.2, `I2CBus` use with `with`-statement
# 2020-10-31, v1.3, generally CircuitPython
# ----------------------------------------------------------------------------
from micropython import const
from busio import SPI, I2C
from busio import UART as _UART

__version__ = "0.1.3.0"

# ----------------------------------------------------------------------------
class SPIBus(object):
  """SPI bus access."""

  def __init__(self, freq, sc, mo, mi=None, spidev=2):
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

  def write(self, wbuf):
    if self._spi.try_lock():
      try:
        self._spi.write(wbuf)
      finally:
        self._spi.unlock()

# ----------------------------------------------------------------------------
class I2CBus(object):
  """I2C bus access."""

  def __init__(self, **kwargs):
    self._i2cDevList = []
    freq = 0
    do_scan = False if not "scan" in kwargs else kwargs["scan"]
    code = 0 if not "code" in kwargs else kwargs["code"]
    scl = kwargs["scl"]
    sda = kwargs["sda"]
    if not code == 0:
      # Default to software implementation of I2C
      from bitbangio import I2C as softI2C
      freq = 400000 if not "freq" in kwargs else kwargs["freq"]
      self._i2c = softI2C(scl=scl, sda=sda, frequency=freq)
      codeStr = "Software"
    else:
      # Hardware implementation ...
      from busio import I2C as hardI2C
      freq = 100000 if not "freq" in kwargs else kwargs["freq"]
      self._i2c = hardI2C(scl=scl, sda=sda, frequency=freq)
      codeStr = "Hardware"
    s = " frequency is {0} kHz".format(freq/1000) if freq > 0 else ""
    print("{0} I2C bus{1}".format(codeStr, s))

    if do_scan:
      try:
        if not self._i2c.try_lock():
          print("ERROR: busio.I2CBus: no lock for scan()")
        else:
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
    self._i2c.writeto(addr, buf)

  def readfrom_into(self, addr, buf):
    self._i2c.readfrom_into(addr, buf)

  def write_then_readinto(self, addr, bufo, bufi, out_start=0, out_end=None,
                          in_start=0, in_end=None, stop_=True):
    self._i2c.writeto(addr, bufo[out_start:out_end])
    buf = bytearray(bufi[in_start:in_end])
    self._i2c.readfrom_into(addr, buf)
    bufi[in_start:in_end] = buf

  def try_lock(self):
    return self._i2c.try_lock()

  def unlock(self):
    self._i2c.unlock()

  def __enter__(self):
    while not self._i2c.try_lock():
      pass
    return self

  def __exit__(self, exc_type, exc_val, exc_tb):
    self._i2c.unlock()
    return False

# ----------------------------------------------------------------------------
class UART(object):
  """UART"""

  def __init__(self, id=1, baudrate=9600, bits=8, parity=None, stop=1, tx=None,
               rx=None, rxbuf=64, timeout=0):
    tout_s = timeout/1000
    self._uart = _UART(tx=tx, rx=rx, baudrate=baudrate, bits=bits,
                       parity=parity, stop=stop, timeout=tout_s,
                       receiver_buffer_size=rxbuf)

  def readline(self):
    return self._uart.readline()

  def write(self, buf):
    return self._uart.write(bytearray(buf))

  def any(self):
    return self._uart.in_waiting

  def deinit(self):
    if self._uart is not None:
      self._uart.deinit()

# ----------------------------------------------------------------------------
