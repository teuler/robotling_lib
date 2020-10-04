# ----------------------------------------------------------------------------
# rmsg.py
# Serial commumication between ESP32 modules.
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-01-05, v1
# ----------------------------------------------------------------------------
try:
  ModuleNotFoundError
except NameError:
  ModuleNotFoundError = ImportError
try:
  # Micropython imports
  import array
  from micropython import const
  from robotling_lib.misc.helpers import timed_function
  from robotling_lib.platform.platform import platform
  if (platform.ID == platform.ENV_ESP32_UPY or
      platform.ID == platform.ENV_ESP32_TINYPICO):
    from machine import UART
  elif (platform.ID == platform.ENV_CPY_SAM51 or
        platform.ID == platform.ENV_CPY_NRF52):
    from busio import UART
  else:
    print("ERROR: No matching hardware libraries in `platform`.")
except ModuleNotFoundError:
  # Standard Python imports
  const = lambda x : x
  import array

__version__   = "0.1.0.0"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
TOK_REM     = 0
# Remark, as a simple text message
# </>REM ArbitraryText;

TOK_VER     = 1
# Information about software version (V) and free space in SRAM (M) in bytes
# >VER;
# <VER V=100 M=1234;

TOK_ERR     = 2
# Returns error code regarding the last message
# with x,      command index, 255=not recognized
#      y,      error code
#      z,      error value (further specifies the error, e.g. an I2C error)
# <ERR C=x E=y,z;

TOK_ACK     = 3
# Acknowledges that command has been executed; when no error occurred and the
# command has no specific response message defined (other than e.g. >ver;)
# with x,      command index
# </>ACK C=x;

TOK_STA     = 4
# Status request ...
# >STA;
#  <STA S=hs,ws,d,sp,sv, lv  #A=a0,a1,...,a4,is,c,ox,oy L=v0,...,v11 P=p0..p7;
#  with hs,     state (`HexState`)
#       ws,     walk engine state (`WEState`)
#       d,      dial state (`DialState`)
#       sp      servo power on/off
#       sv,     servo voltage in mV
#       lv,     logic voltage in mV
'''
//       tv,     ms since last update of voltages
//       ta,     ms since last update of analog inputs
//       t,      ms since last STA message
//       a0..a4, analog sensor readings
//       is,     current sensor reading
//       c,      compass reading, in degrees (0..359)
//       ox,oy   odometry, change in position since last call, in mm
//       v0..v11 servo load readings, two per leg
//       p0..p17 leg positions, as angles in degree x10
'''

TOK_XP0     = 5
# Move all servos to the default positions
# >XP0;
# <ACK C=5;

TOK_GG0     = 6
# Prepare the gait generator (GGN)
# with a=1/0/-1   GGN on/off/off+reset
#      m,         mode; 1=translation, 2=walk, 3=single leg, 4=rotate
#      g,         gait type, 0=default
# >GG0 M=a,m G=g;
# <ACK C=<command>;

TOK_GGE     = 7
# Perform an emergency stop
# >GGE;
# <ACK C=<command>;

TOK_GGP     = 8
# Change walk parameters of the gait generator (GGN), positions etc.
# with bo,        bodyYOffs; 0=down, 35=default up
#      bs,        bodyYShift; ...
#      px,pz,     bodyPos; global body position
#      bx,by,bz   bodyRot; global input pitch (X), rotation (Y) and
#                 roll (Z) of the body
#      lh,        legLiftHeight; current travel height
#      tx,tz      travelLen; current travel length X,Z
#      ty         travelRotY; current travel rotation Y
# >GGP B=bs,px,pz,bx,by,bz T=bo,lh,tx,tz,ty;
# <ACK C=<command>;

TOK_GGT     = 9
'''
- Change walk parameters of the gait generator (GGN), timing
  with ds,        delaySpeed_ms; ddjustible delay in ms
       di,        delayInput; delay that depends on the input to get
                  the "sneaking" effect (??, not yet used)
  >GGT D=ds,di;
  <ACK C=<command>;
'''

TOK_GGQ     = 10
# Change only most important walk parameters and request status quickly
# with bo,        bodyYOffs; 0=down, 35=default up
#      lh,        legLiftHeight; current travel height
#      tx,tz,     travelLen; current travel length X,Z
#      ty,        travelRotY; current travel rotation Y
#      ds,        delaySpeed_ms; ddjustible delay in ms
#      ta         target angle (in degrees) as compass reading when
#                 rotating the robot (using GGN_travelRotY)
# >GGQ T=bo,lh,tx,tz,ty D=ds A=ta;
# <STA ...;

TOK_LastInd = 10

TOK_NONE    = 255
TOK_StrList = ["REM", "VER", "ERR", "ACK", "STA", "XP0",
               "GG0", "GGE", "GGP", "GGT", "GGQ"]

TOK_StrLength          = const(3)
TOK_MinParamStrLength  = const(3)
TOK_MaxParams          = const(4)
TOK_MaxData            = const(18)
TOK_MaxMsgLen_bytes    = const(154)
TOK_MinMsgLen_bytes    = const(6)

MSG_Client             = ">"
MSG_Host               = "<"
MSG_EndChr             = ";"
MSG_DataSepChr         = ","

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Error codes
class Err():
  Ok                     = const(0)
  CmdNotRecognized       = const(1)
  AtLeastOneInvalidParam = const(3)
  InvalidOrTooFewParams  = const(4)
  CmdNotImplemented      = const(5)
  DeviceNotReady         = const(6)
  TooManyParamsOrData    = const(7)
  CmdStrIncomplete       = const(8)
  Unknown                = const(9)

class PortType():
  NONE                   = const(0)
  BLE_MPY                = const(1)
  BLE_PC                 = const(2)
  UART_MPY               = const(3)
  COM_PC                 = const(4)
  I2C_MPY                = const(5)

# ----------------------------------------------------------------------------
class RMsg(object):
  """A simple string-based interboard message format."""

  def __init__(self):
    """ Initialize message content
    """
    self._paramCh = bytearray(TOK_MaxParams)
    self._nData = bytearray(TOK_MaxData)
    self._poll = None
    self._portType = PortType.NONE
    self.reset(clearBuf=True)

  def reset(self, clearBuf=False):
    """ Reset message content
    """
    self._tok = TOK_NONE
    self._nParams = 0
    self._sOut = ""
    self._sIn = ""
    if clearBuf:
      self._sInBuf = ""
    self._data = []
    self._errC = Err.Ok

  @property
  def port_type(self):
    return self._portType

  @property
  def token(self):
    return self._tok

  @property
  def out_message_str(self):
    return self._sOut

  @token.setter
  def token(self, val):
    self.errC = Err.Ok
    if val < 0 or val > TOK_LastInd:
      self._tok = TOK_NONE
      self._errC = Err.CmdNotRecognized
    else:
      self._tok = val

  @property
  def error(self):
    return self._errC

  def __getitem__(self, iKD):
    if iKD[0] >= 0 and iKD[0] < self._nParams and iKD[1] < self._nData[iKD[0]]:
      return self._data[iKD[0]][iKD[1]]
    else:
      return None

  def __setitem__(self, iKD, val):
    if iKD[0] >= 0 and iKD[0] < self._nParams and iKD[1] < self._nData[iKD[0]]:
      self._data[iKD[0]][iKD[1]] = val

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def add_data(self, key, data):
    """ Add a parameter key with data
    """
    i = self._nParams
    self._paramCh[i] = ord(key[0])
    self._nData[i] = len(data)
    self._data.append(array.array("i", data))
    self._nParams += 1

  def to_string(self, isClient=True):
    """ Generate string from message content
    """
    self._errC = Err.Ok
    self._sOut = ""
    if self._tok < 0 or self._tok > TOK_LastInd:
      self._errC = Err.CmdNotRecognized
    elif self._nParams >= TOK_MaxParams or len(self._data) > TOK_MaxData:
      self._errC = Err.TooManyParamsOrData
    else:
      # Put together the message content as a string ready to send
      s0 = (MSG_Client if isClient else MSG_Host) +TOK_StrList[self._tok]
      if self._nParams > 0:
        s1 = " "
        for iP in range(self._nParams):
          s1 += chr(self._paramCh[iP]) +"="
          s1 += self._data_as_str(iP)
          s1 += " " if iP<self._nParams-1 else MSG_EndChr
      else:
        s1 = MSG_EndChr
      self._sOut = s0 +s1
    return self._sOut

  def from_string(self, sMsg):
    """ Parse string into message
    """
    self.reset()
    if not (sMsg[0] in [MSG_Client, MSG_Host]  and sMsg[-1] == MSG_EndChr):
      self._errC = Err.CmdStrIncomplete
    else:
      # Get and identify token
      sTok = sMsg[1:TOK_StrLength+1].upper()
      if not sTok in TOK_StrList:
        self._errC = Err.CmdNotRecognized
      else:
        # Get token ID and then parameters, if any
        self._tok = TOK_StrList.index(sTok)
        data = sMsg[2+TOK_StrLength:-1].split()
        if len(data) > 0:
          try:
            # Get data ...
            for i, s in enumerate(data):
              self._paramCh[i] = ord(s[0])
              vals = [int(v) for v in s[2:].split(MSG_DataSepChr)]
              self._nData[i] = len(vals)
              self._data.append(array.array("i", vals))
              self._nParams += 1
          except ValueError:
            self._errC = Err.AtLeastOneInvalidParam
    return self._errC

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _data_as_str(self, iParam):
    return "".join("{0:d}{1}".format(i,
                   MSG_DataSepChr if j<self._nData[iParam]-1 else "")
                   for j,i in enumerate(self._data[iParam]))

  def __repr__(self):
    if self._tok >= 0 and self._tok <= TOK_LastInd:
      s = "token={0}".format(TOK_StrList[self._tok])
      if self._nParams > 0:
        s += ", "
        for iP in range(self._nParams):
          s += "{0}={1} ".format(chr(self._paramCh[iP]), self._data_as_str(iP))
      return s
    else:
      return "n/a"

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def send(self, tout_ms=100):
    """ Send message as string using the respective serial interface and
        returns the reply, if any, as a string. Accepts a timeout in [ms]
    """
    self._errC = Err.Ok
    self._sIn = ""
    if self._tok < 0 or self._tok > TOK_LastInd:
      self._errC = Err.CmdNotRecognized
    else:
      self.to_string(self.isClient)
      if len(self._sOut) > 0:
        try:
          self.write(self._sOut)
          if tout_ms > 0:
            if self._poll:
              res = self._poll(tout_ms)
            repl = self.readline()
            self._sIn = repl.decode()
        except:
          # TODO: Catch different exceptions
          self._errC = Err.Unknown
    return self._sIn

  def receive(self, tout_ms=50):
    """ Read from serial connection and check if a complete message is
        available. Returns an error code
    """
    self._errC = Err.Ok
    if self.any() > 0:
      # Characters are waiting; add them to the buffer
      self._sInBuf += self.read().decode()

    if len(self._sInBuf) < TOK_MinMsgLen_bytes:
      # Too few characters for a complete message
      return False

    # May contain a complete message
    tmp = self._sInBuf.split(MSG_Client)
    n = len(tmp)
    if n == 1:
      # No start character ...
      return False

    if MSG_EndChr in tmp[1]:
      # Contains a complete message
      msg = MSG_Client +tmp[1].split(MSG_EndChr)[0] +MSG_EndChr
      self._errC = self.from_string(msg)
      self._sInBuf = MSG_Client +MSG_Client.join(tmp[2:])
      return self._errC == Err.Ok

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def deinit(self):
    pass

# ----------------------------------------------------------------------------
class RMsgUARTMPy(RMsg):
  """A simple string-based interboard message format using a serial UART
     under MicroPython."""

  def __init__(self, uart, isClient=True):
    super().__init__()
    self._uart = uart
    self.isClient = isClient
    try:
      import select
      self.pollObj = select.poll()
      self.pollObj.register(self._uart, select.POLLIN)
      self._poll = self._poll_via_select
    except ImportError:
      self.pollObj = None
      self._poll = None
    self.write = self._write
    self.read = self._read
    self.readline = self._readline
    self.any = self._any
    self._portType = PortType.UART_MPY

  @property 
  def isConnected(self):
     return self.self._uart is not None

  def _write(self, s):
    self._uart.write(s)

  def _poll_via_select(self, tout_ms):
    return self.pollObj.poll(tout_ms)

  def _read(self):
    return self._uart.read()

  def _readline(self):
    return self._uart.readline()

  def _any(self):
    return self._uart.any()

# ----------------------------------------------------------------------------
class RMsgBLEMPy(RMsg):
  """A simple string-based interboard message format using a serial BLE
     peripheral protocol under MicroPython."""

  #def __init__(self, name="ble-uart", isClient=True):
  def __init__(self, bsp, isClient=True):
    super().__init__()
    self.isClient = isClient
    self._bsp = bsp
    self.write = self._bsp.write
    self.read = self._bsp.read
    self.readline = self._bsp.read
    self.any = self._any
    self._portType = PortType.BLE_MPY

  @property
  def isConnected(self):
     return self._bsp.is_connected

  def _any(self):
    return len(self._bsp.rx_buffer)

# ----------------------------------------------------------------------------
class RMsgCOM(RMsg):
  """A simple string-based interboard message format using a serial port
     under Windows/Linux."""

  def __init__(self, com, baudrate, timeout=1.0, isClient=True):
    super().__init__()
    self._com = com
    self._baudrate = baudrate
    self.isClient = isClient
    try:
      import serial
      self.serClient = serial.Serial(com, baudrate, timeout=timeout)
      self.serClient.flushInput()
      self.serClient.flushOutput()
      self._isConnected = self.serClient.isOpen()
      self.write = self._write
      self.read = self._read
      self.readline = self._readline
      self.any = self._any
      self._portType = PortType.COM_PC
    except serial.SerialException as e:
      print("ERROR: Could not open {0}".format(com))

  @property
  def isConnected(self):
     self._isConnected = self.serClient.isOpen()
     return self._isConnected

  def _write(self, s):
    self.serClient.write(s.encode('utf-8') +b"\n")

  def _read(self):
    return self.serClient.read().decode()

  def _readline(self):
    return self.serClient.read_until()

  def _any(self):
    return self.serClient.in_waiting

  def deinit(self):
    if self.serClient:
      self.serClient.close()

# ----------------------------------------------------------------------------
