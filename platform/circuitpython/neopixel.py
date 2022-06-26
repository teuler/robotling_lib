# ----------------------------------------------------------------------------
# neopixel.py
#
# Basic NeoPixel support
# (for CircuitPython)
#
# The MIT License (MIT)
# Copyright (c) 2018-2020 Thomas Euler
# 2018-09-26, v1
# 2020-10-31, v1.1, generally CircuitPython
# ----------------------------------------------------------------------------
from robotling_lib.platform.circuitpython.other.neopixel \
  import NeoPixel as NeoPixelBase

__version__ = "0.1.1.0"

# ----------------------------------------------------------------------------
class NeoPixel(NeoPixelBase):
  """Basic NeoPixel class"""

  def __init__(self, pin, nNPs=1):
    """ Requires a pin index and the number of NeoPixels
    """
    super().__init__(pin, nNPs)

  def set(self, rgb, iNP=0, show=False):
    """ Takes an RGB value as a tupple for the NeoPixel with the index `iNP`,
        update all NeoPixels if `show`==True
    """
    self.__setitem__(iNP, tuple(rgb))
    if show:
      self.show()

# ----------------------------------------------------------------------------
