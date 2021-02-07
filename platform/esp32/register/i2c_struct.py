# ----------------------------------------------------------------------------
# i2c_struct.py
#
# The MIT License (MIT)
# Copyright (c) 2030 Thomas Euler
# 2020-01-04, v1
#
# Based on the CircuitPython driver:
# https://github.com/adafruit/Adafruit_CircuitPython_Register
# Generic structured registers based on `struct`
# Author(s): Scott Shawcroft
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Adafruit Industries
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
# pylint: disable=too-few-public-methods
# ----------------------------------------------------------------------------
try:
  import struct
except ImportError:
  import ustruct as struct

class Struct:
  """
  Arbitrary structure register that is readable and writeable.
  Values are tuples that map to the values in the defined struct.  See struct
  module documentation for struct format string and its possible value types.
  :param int register_address: The register address to read the bit from
  :param type struct_format: The struct format string for this register.
  """
  def __init__(self, register_address, struct_format):
    self.format = struct_format
    self.address = register_address

  def __get__(self, obj, objtype=None):
    b = bytearray(1 +struct.calcsize(self.format))
    b[0] = self.address
    addr = obj._i2c_addr
    obj.i2c_device.write_then_readinto(addr, b, b, out_end=1, in_start=1, stop_=False)
    return struct.unpack_from(self.format, memoryview(b)[1:])

  def __set__(self, obj, value):
    b = bytearray(1 +struct.calcsize(self.format))
    b[0] = self.address
    struct.pack_into(self.format, b, 1, *value)
    obj.i2c_device.writeto(obj._i2c_addr, b)

class UnaryStruct:
  """
  Arbitrary single value structure register that is readable and writeable.
  Values map to the first value in the defined struct.  See struct
  module documentation for struct format string and its possible value types.
  :param int register_address: The register address to read the bit from
  :param type struct_format: The struct format string for this register.
  """
  def __init__(self, register_address, struct_format):
    self.format = struct_format
    self.address = register_address

  def __get__(self, obj, objtype=None):
    b = bytearray(1 +struct.calcsize(self.format))
    b[0] = self.address
    addr = obj._i2c_addr
    obj.i2c_device.write_then_readinto(addr, b, b, out_end=1, in_start=1, stop_=False)
    return struct.unpack_from(self.format, b, 1)[0]

  def __set__(self, obj, value):
    b = bytearray(1 +struct.calcsize(self.format))
    b[0] = self.address
    struct.pack_into(self.format, b, 1, value)
    obj.i2c_device.writeto(obj._i2c_addr, b)

'''
class ROUnaryStruct(UnaryStruct):
  """
  Arbitrary single value structure register that is read-only.
  Values map to the first value in the defined struct.  See struct
  module documentation for struct format string and its possible value types.
  :param int register_address: The register address to read the bit from
  :param type struct_format: The struct format string for this register.
  """
  def __set__(self, obj, value):
    raise AttributeError()
'''
# ----------------------------------------------------------------------------
