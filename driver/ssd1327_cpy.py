# ----------------------------------------------------------------------------
# sdd1327_cpy.py
# Class for SSD1327 OLED display (I2C), CircuitPython version
#
# The MIT License (MIT)
# Copyright (c) 2021 Thomas Euler
# 2021-01-01, v1
#
# Requires the following original Adafruit libraries in `lib`:
# - adafruit_display_text (folder)
# - adafruit_display_shapes (folder)
#
# Based on the CircuitPython SSD1327 OLED I2C driver `adafruit_ssd1327`
# https://github.com/mcauser/micropython-ssd1327
#
# The MIT License (MIT)
# Copyright (c) 2019 Scott Shawcroft for Adafruit Industries
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
import robotling_lib.misc.ansi_color as ansi
from robotling_lib.platform.platform import platform
if platform.languageID == platform.LNG_CIRCUITPYTHON:
  import displayio
  import terminalio
  from adafruit_display_shapes.rect import Rect
  from adafruit_display_shapes.circle import Circle
  from adafruit_display_shapes.line import Line
  from adafruit_display_text.label import Label
  import robotling_lib.platform.circuitpython.time as time
else:
  print(ansi.RED +"ERROR: This is a CircutPython-only library." +ansi.BLACK)

__version__ = "0.1.0.0"
CHIP_NAME   = "ssd1327"

# pylint: disable=bad-whitespace
_ADDR_SSD1327        = const(0x3C)
_MAX_GROUPS          = const(32)
_MAX_COLORS          = const(4)

REG_CMD              = const(0x80)
SET_DISP_MODE        = const(0xA4)
SET_CONTRAST         = const(0x81)
SET_FN_SELECT_A      = const(0xAB)
SET_DISP             = const(0xAE)
SET_SCROLL_DISABLE   = const(0x2E)
SET_SCROLL_ENABLE    = const(0x2F)

_INIT_SEQUENCE = (
    b"\xAE\x00"      # DISPLAY_OFF
    b"\x81\x01\x80"  # set contrast control
    b"\xa0\x01\x53"  # remap memory, odd even columns, com flip and column swap
    b"\xa1\x01\x00"  # Display start line is 0
    b"\xa2\x01\x00"  # Display offset is 0
    b"\xa4\x00"      # Normal display
    b"\xa8\x01\x3f"  # Mux ratio is 1/64
    b"\xb1\x01\x11"  # Set phase length
    b"\xb8\x0f\x00"
    b"\x01\x02\x03"
    b"\x04\x05\x06"
    b"\x07\x08\x10"
    b"\x18\x20\x2f"
    b"\x38\x3f"     # Set graytable
    b"\xb3\x01\x00"  # Set dclk to 100hz
    b"\xab\x01\x01"  # enable internal regulator
    b"\xb6\x01\x04"  # Set second pre-charge period
    b"\xbe\x01\x0f"  # Set vcom voltage
    b"\xbc\x01\x08"  # Set pre-charge voltage
    b"\xd5\x01\x62"  # function selection B
    b"\xfd\x01\x12"  # command unlock
    b"\xAF\x00"      # DISPLAY_ON
)
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
# pylint: disable=too-few-public-methods
class SSD1327(displayio.Display):
  """SSD1327 driver"""

  def __init__(self, bus, **kwargs):
    # Patch the init sequence for 32 pixel high displays.
    init_sequence = bytearray(_INIT_SEQUENCE)
    height = kwargs["height"]
    if "rotation" in kwargs and kwargs["rotation"] % 180 != 0:
      height = kwargs["width"]
    init_sequence[18] = height - 1  # patch mux ratio
    auto = True if not kwargs["auto_refresh"] else kwargs["auto_refresh"]
    super().__init__(
      bus,
      init_sequence,
      **kwargs,
      color_depth=4,
      grayscale=True,
      set_column_command=0x15,
      set_row_command=0x75,
      data_as_commands=True,
      single_byte_bounds=True,
    )
    auto = True if not kwargs["auto_refresh"] else kwargs["auto_refresh"]
    self.auto_refresh = auto

# ----------------------------------------------------------------------------
class SSD1327_I2C(object):
  """SSD1327 driver (I2C)"""

  def __init__(self, i2c, w=128, h=128, addr=_ADDR_SSD1327,
               auto_refresh=True, rotation_deg=90):
    # Initialize
    self.i2c_device = i2c
    self._i2c_addr = addr
    self._height = h
    self._width = w
    self._border = 8
    self._fontscale = 1
    self._tCol = _MAX_COLORS -1
    self._bCol = 0
    self._tyPos = 0
    self._font = terminalio.FONT
    dxy = self._font.get_bounding_box()
    self._tdx = dxy[0]
    self._tdy = dxy[1]
    self._power = True

    # Generate actual display object
    displayio.release_displays()
    self._displayBus = displayio.I2CDisplay(i2c.bus, device_address=addr)
    self._display = SSD1327(self._displayBus, width=w, height=h,
                            auto_refresh=auto_refresh, rotation=rotation_deg)
    # Generate graphic tools
    self._bmp = displayio.Bitmap(w, h, _MAX_COLORS)
    self._pal = displayio.Palette(_MAX_COLORS)
    self._pal[0] = 0x000000
    self._pal[1] = 0x555555
    self._pal[2] = 0xAAAAAA
    self._pal[3] = 0xFFFFFF
    self._tgrid = displayio.TileGrid(self._bmp, pixel_shader=self._pal)
    self._group = displayio.Group(max_size=_MAX_GROUPS)
    self._group.append(self._tgrid)
    self.show()
    self.isReady = True

  def deinit(self):
    """ Deinitialize display and power off
    """
    self.power = False
    displayio.release_displays()
    self.isReady = False

  #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def auto_refresh(self):
    """ Auto-refresh or not
    """
    return self._display.auto_refresh

  @auto_refresh.setter
  def auto_refresh(self, state):
    self._display.auto_refresh = state

  @property
  def power(self):
    """ Power status of the display
    """
    return self._power

  @power.setter
  def power(self, state):
    if state:
      buf = bytearray([SET_FN_SELECT_A, 0x01, SET_DISP | 0x01])
    else:
      buf = bytearray([SET_FN_SELECT_A, 0x00, SET_DISP])
    self._displayBus.send(REG_CMD, buf)

  @property
  def size(self):
    return self._width, self._height

  @property
  def group(self):
    return self._group

  @property
  def text_color(self):
    """ Current text color
    """
    return self._tCol

  @text_color.setter
  def text_color(self, col):
    self._tCol = min(col, _MAX_COLORS-1)

  @property
  def bkg_color(self):
    """ Current background color for text
    """
    return self._bCol

  @bkg_color.setter
  def bkg_color(self, col):
    self._bCol = min(col, _MAX_COLORS-1)

  @property
  def font_height(self):
    return self._tdy

  #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def show(self):
    """ Show result of recent drawing commands
    """
    self._display.show(self._group)

  def refresh(self):
    """ Force display refresh
    """
    self._display.refresh()

  def clear(self):
    """ Clear group from objects
    """
    while len(self._group) > 1:
      self._group.pop()

  def fill(self, col, clear_groups=True):
    """ Fill screen with color `col` (in [0.._MAX_COLORS-1]); if `clear_groups`
        is True the remove all layers except the bitmap layer from the object's
        group
    """
    col = min(col, _MAX_COLORS-1)
    self._bmp.fill(col)
    self._tyPos = 0
    self._bCol = col
    if clear_groups:
      self.clear()

  def contrast(self, contrast):
    """ Set contrast, with `contrast` in [0..255]
    """
    buf = bytearray([SET_CONTRAST, min(contrast, 255)])
    self._displayBus.send(REG_CMD, buf)

  def invert(self, invert):
    """ Invert display
    """
    buf = bytearray([SET_DISP_MODE | (invert & 1) << 1 | (invert & 1)])
    self._displayBus.send(REG_CMD, buf)

  def pixel(self, x, y, col):
    """ Draw a pixel
    """
    self._bmp[x, y] = min(col, _MAX_COLORS-1)

  def circle(self, x, y, r, fill=None, outline=None, stroke=1, index=None):
    """ Draw a circle
    """
    fl = self._pal[fill] if fill else None
    ol = self._pal[outline] if outline else None
    c = Circle(x, y, r, fill=fl, outline=ol, stroke=stroke)
    if index:
      self._group.insert(index, c)
    else:
      self._group.append(c)
    return c

  def rect(self, x, y, w, h, fill=None, outline=None, stroke=1, index=None):
    """ Draw a rectangle
    """
    fl = self._pal[fill] if fill else None
    ol = self._pal[outline] if outline else None
    r = Rect(x, y, w, h, fill=fl, outline=ol, stroke=stroke)
    if index:
      self._group.insert(index, r)
      print(len(self._group), index)
    else:
      self._group.append(r)
    return r

  def line(self, x0, y0, x1, y1, col, index=None):
    """ Draw a line
    """
    c = self._pal[min(col, _MAX_COLORS-1)]
    l = Line(x0, y0, x1, y1, c)
    if index:
      self._group.insert(index, l)
    else:
      self._group.append(l)
    return l

  def text(self, txt, x, y, tcol=None, bcol=None, btransparent=False):
    """ Print text at pixel position `x,y`, demarking the top-left corner
        of the text field
    """
    tc = self._pal[self._tCol] if tcol is None else self._pal[tcol]
    if btransparent:
      bc = None
    else:
      bc = self._pal[self._bCol] if bcol is None else self._pal[bcol]
    y1 = int(y +self._tdy //2)
    x1 = int(x)
    ta = Label(self._font, x=x1, y=y1, color=tc, background_color=bc, text=txt)
    self._group.append(ta)
    return ta

  def println(self, txt, show=True):
    y = self._tyPos
    dy = self._tdy
    self.text(txt, 0, y)
    if self._tyPos > self._height -dy:
      '''
      self._framebuf.scroll(0, -8)
      '''
      self.rect(0, y, self._width-1, y +dy, fill=self._bCol)
    else:
      self._tyPos += dy
    if show:
      self.show()

  """
  def scroll(self, dx, dy):
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = y1 +dy
    sp = 1
    buf = bytearray([SET_SCROLL_DISABLE, 0x26, 0, 0, y1, sp, y2,
                     x1 >> 1, x2 >> 1, 0])
    # dir 0x26 oder 0x27
    self._displayBus.send(REG_CMD, buf)
    buf = bytearray([SET_SCROLL_ENABLE])
    self._displayBus.send(REG_CMD, buf)
    time.sleep_ms(550)
    buf = bytearray([SET_SCROLL_DISABLE])
    self._displayBus.send(REG_CMD, buf)
  """
  """
  def rotate(self, rotate):
    if self.isReady:
      self.poweroff()
      self.__write_cmd(SET_DISP_OFFSET)
      # 0x20=0 degrees, 0x60=180 degrees
      self.__write_cmd(0x60 if rotate else 0x20)
      self.__write_cmd(SET_SEG_REMAP)
      # 0x51=0 degrees, 0x42=180 degrees
      self.__write_cmd(0x42 if rotate else 0x51)
      self.poweron()

  def lookup(self, table):
    if self.isReady:
      # GS0 has no pre-charge and current drive
      self.__write_cmd(SET_GRAYSCALE_TABLE)
      for i in range(0, 15):
        self.__write_cmd(table[i])
  """
# ----------------------------------------------------------------------------
