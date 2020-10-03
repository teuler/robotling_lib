"""
MicroPython SSD1327 OLED I2C driver
https://github.com/mcauser/micropython-ssd1327

MIT License
Copyright (c) 2017 Mike Causer

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# ----------------------------------------------------------------------------
from micropython import const
from framebuf import FrameBuffer, GS4_HMSB

__version__ = "0.1.0.0"
CHIP_NAME   = "ssd1327"

# pylint: disable=bad-whitespace
_ADDR_SSD1327         = const(0x3C)

# Commands
SET_COL_ADDR          = const(0x15)
SET_SCROLL_DEACTIVATE = const(0x2E)
SET_ROW_ADDR          = const(0x75)
SET_CONTRAST          = const(0x81)
SET_SEG_REMAP         = const(0xA0)
SET_DISP_START_LINE   = const(0xA1)
SET_DISP_OFFSET       = const(0xA2)
SET_DISP_MODE         = const(0xA4) # 0xA4 normal, 0xA5 all on, 0xA6 all off, 0xA7 when inverted
SET_MUX_RATIO         = const(0xA8)
SET_FN_SELECT_A       = const(0xAB)
SET_DISP              = const(0xAE) # 0xAE power off, 0xAF power on
SET_PHASE_LEN         = const(0xB1)
SET_DISP_CLK_DIV      = const(0xB3)
SET_SECOND_PRECHARGE  = const(0xB6)
SET_GRAYSCALE_TABLE   = const(0xB8)
SET_GRAYSCALE_LINEAR  = const(0xB9)
SET_PRECHARGE         = const(0xBC)
SET_VCOM_DESEL        = const(0xBE)
SET_FN_SELECT_B       = const(0xD5)
SET_COMMAND_LOCK      = const(0xFD)

# Registers
REG_CMD               = const(0x80)
REG_DATA              = const(0x40)
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class SSD1327:
  def __init__(self, width, height, external_vcc, buf):
    self._width = width
    self._height = height
    self._external_vcc = external_vcc
    if not buf:
      self._buffer = bytearray(self._width *self._height //2)
    else:
      self._buffer = buf
    self._framebuf = FrameBuffer(self._buffer, width, height, GS4_HMSB)
    self.isReady = True
    self.poweron()
    self.__init_display()

  def __init_display(self):
    for cmd in (
      SET_COMMAND_LOCK, 0x12, # Unlock
      SET_DISP, # Display off
      # Resolution and layout
      SET_DISP_START_LINE, 0x00,
      SET_DISP_OFFSET, 0x00, # Set vertical offset by COM from 0~127
      # Set re-map
      # Enable column address re-map
      # Disable nibble re-map
      # Horizontal address increment
      # Enable COM re-map
      # Enable COM split odd even
      SET_SEG_REMAP, 0x51,
      SET_MUX_RATIO, self._height - 1,
      # Timing and driving scheme
      SET_FN_SELECT_A, 0x01, # Enable internal VDD regulator
      SET_PHASE_LEN, 0x51, # Phase 1: 1 DCLK, Phase 2: 5 DCLKs
      SET_DISP_CLK_DIV, 0x01, # Divide ratio: 1, Oscillator Frequency: 0
      SET_PRECHARGE, 0x08, # Set pre-charge voltage level: VCOMH
      SET_VCOM_DESEL, 0x07, # Set VCOMH COM deselect voltage level: 0.86*Vcc
      SET_SECOND_PRECHARGE, 0x01, # Second Pre-charge period: 1 DCLK
      SET_FN_SELECT_B, 0x62, # Enable enternal VSL, Enable second precharge
      # Display
      SET_GRAYSCALE_LINEAR, # Use linear greyscale lookup table
      SET_CONTRAST, 0x7f, # Medium brightness
      SET_DISP_MODE, # Normal, not inverted
      # 96x96:
      # SET_ROW_ADDR, 0 95,
      # SET_COL_ADDR, 8, 55,
      # 128x128:
      # SET_ROW_ADDR, 0 127,
      # SET_COL_ADDR, 0, 63,
      SET_ROW_ADDR, 0x00, self._height -1,
      SET_COL_ADDR, ((128 -self._width) //4), 63 -((128 -self._width) //4),
      SET_SCROLL_DEACTIVATE,
      SET_DISP | 0x01): # Display on
      self.__write_cmd(cmd)
    self.fill(0)
    self.show()

  def deinit(self):
    self._framebuf = None
    self._buffer = None
    self.isReady = False

  def poweroff(self):
    if self.isReady:
      self.__write_cmd(SET_FN_SELECT_A)
      self.__write_cmd(0x00) # Disable internal VDD regulator, to save power
      self.__write_cmd(SET_DISP)

  def poweron(self):
    if self.isReady:
      self.__write_cmd(SET_FN_SELECT_A)
      self.__write_cmd(0x01) # Enable internal VDD regulator
      self.__write_cmd(SET_DISP | 0x01)

  def contrast(self, contrast):
    if self.isReady:
      self.__write_cmd(SET_CONTRAST)
      self.__write_cmd(contrast) # 0-255

  def invert(self, invert):
    if self.isReady:
      # 0xA4=Normal, 0xA7=Inverted
      self.__write_cmd(SET_DISP_MODE | (invert & 1) << 1 | (invert & 1))

  def show(self):
    if self.isReady:
      self.__write_cmd(SET_COL_ADDR)
      self.__write_cmd((128 -self._width) //4)
      self.__write_cmd(63 -((128 -self._width) //4))
      self.__write_cmd(SET_ROW_ADDR)
      self.__write_cmd(0x00)
      self.__write_cmd(self._height -1)
      self.__write_data(self._buffer)

  def fill(self, col):
    if self.isReady:
      self._framebuf.fill(col)

  def pixel(self, x, y, col):
    if self.isReady:
      self._framebuf.pixel(x, y, col)

  def scroll(self, dx, dy):
    if self.isReady:
      # software scroll
      self._framebuf.scroll(dx, dy)

  def text(self, string, x, y, col=15):
    if self.isReady:
      self._framebuf.text(string, x, y, col)

# ----------------------------------------------------------------------------
class SSD1327_I2C(SSD1327):
  def __init__(self, w, h, i2c, addr=_ADDR_SSD1327, ext_vcc=False, buf=None):
    self._i2c = i2c
    self._addr = addr
    super().__init__(w, h, ext_vcc, buf)

  def __write_cmd(self, cmd):
    # Co=1, D/C#=0
    temp = bytearray([REG_CMD, cmd])
    self._i2c.writeto(self._addr, bytearray([REG_CMD, cmd]))

  def __write_data(self, buf):
    # Co=0, D/C#=1
    temp = bytearray([self._addr << 1, REG_DATA])
    self._i2c.start()
    self._i2c.write(temp)
    self._i2c.write(buf)
    self._i2c.stop()

  '''
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
  '''

# ----------------------------------------------------------------------------
