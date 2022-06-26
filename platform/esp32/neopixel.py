# ----------------------------------------------------------------------------
# neopixel.py
#
# Basic NeoPixel support
# (for standard micropython, ESP32, as HUZZAH32 feather)
#
# The MIT License (MIT)
# Copyright (c) 2018 Thomas Euler
# 2018-09-26, v1
# 2020-11-14, v1.1, `getColorFromWheel` added
# ----------------------------------------------------------------------------
from neopixel import NeoPixel as NeoPixelBase
from machine import Pin

__version__ = "0.1.1.0"

# ----------------------------------------------------------------------------
class NeoPixel(NeoPixelBase):
  """Basic NeoPixel class"""

  def __init__(self, pin, nNPs=1):
    """ Requires a pin index and the number of NeoPixels
    """
    super().__init__(Pin(pin, Pin.OUT), nNPs, bpp=3)

  def set(self, rgb, iNP=0, show=False):
    """ Takes an RGB value as a tupple for the NeoPixel with the index `iNP`,
        update all NeoPixels if `show`==True
    """
    self.__setitem__(iNP, rgb)
    if show:
      self.write()

  def show(self):
    self.write()

  def getColorFromWheel(self, iWheel):
    """ Get an RGB color from a wheel-like color representation
    """
    iWheel = iWheel % 255
    if iWheel < 85:
      return (255 -iWheel*3, 0, iWheel*3)
    elif iWheel < 170:
      iWheel -= 85
      return (0, iWheel*3, 255 -iWheel*3)
    else:
      iWheel -= 170
      return (iWheel*3, 255 -iWheel*3, 0)

# ----------------------------------------------------------------------------
