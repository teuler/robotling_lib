# ----------------------------------------------------------------------------
# rmsg.py
# Serial commumication between ESP32 modules.
#
# The MIT License (MIT)
# Copyright (c) 2020-21 Thomas Euler
# 2020-01-05, v1
# 2020-10-31, v1.2, Use `languageID` instead of `ID`
# 2021-01-18, v1.3, - Improved sending speed via optimized code
#                   - Calibration commend added (`CAL`)
# 2021-02-01, v1.4, Switched to binary format for efficiency
# 2021-06-13, v1.5, - some bug fixes
#                   - memory in KBytes
# ----------------------------------------------------------------------------
try:
  ModuleNotFoundError
except NameError:
  ModuleNotFoundError = ImportError
try:
  # Micropython imports
  import array
  import binascii
  from micropython import const
  from robotling_lib.misc.helpers import timed_function
  import robotling_lib.misc.ansi_color as ansi
  from robotling_lib.platform.platform import platform
except ModuleNotFoundError:
  # Standard Python imports
  const = lambda x : x
  import array

__version__   = "0.1.5.0"

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
TOK_REM     = const(0)
# Remark, as a simple text message
# </>REM ArbitraryText;

TOK_VER     = const(1)
# Information about software version (V) and free space in SRAM (M) in KBytes
# >VER;
# <VER V=100 M=1234;

TOK_ERR     = const(2)
# Returns error code regarding the last message
# with x,      command index, 255=not recognized
#      y,      error code
#      z,      error value (further specifies the error, e.g. an I2C error)
# <ERR C=x E=y,z;

TOK_ACK     = const(3)
# Acknowledges that command has been executed; when no error occurred and the
# command has no specific response message defined (other than e.g. >ver;)
# with x,      command index
# </>ACK C=x;

TOK_STA     = const(4)
STA_S_LEN   = const(23)
# Status request ...
# >STA;
#  <STA S=hs,ws,d,sp,sv,lv, hd,pt,rl, l0..l7, f0..f6;
#  with hs,     state (`HexState`)
#       ws,     walk engine state (`WEState`)
#       d,      dial state (`DialState`)
#       sp      servo power on/off
#       sv,     servo voltage in mV
#       lv,     logic voltage in mV
#       hd,p,r  compass heading, pitch and roll ([°])
#       l0..l7  servo load channels #0 to #7
#       f0..f6  foot positions (just y)
'''
//       tv,     ms since last update of voltages
//       ta,     ms since last update of analog inputs
//       t,      ms since last STA message
//       ox,oy   odometry, change in position since last call, in mm
'''

TOK_XP0     = const(5)
# Move all servos to the default positions
# >XP0;
# <ACK C=5;

TOK_GG0     = const(6)
# Prepare the gait generator (GGN)
# with a=1/0/-1   GGN on/off/off+reset
#      m,         mode; 1=translation, 2=walk, 3=single leg, 4=rotate
#      g,         gait type, 0=default
# >GG0 M=a,m G=g;
# <ACK C=<command>;

TOK_GGE     = const(7)
# Perform an emergency stop
# >GGE;
# <ACK C=<command>;

TOK_GGP     = const(8)
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

TOK_GGT     = const(9)
'''
- Change walk parameters of the gait generator (GGN), timing
  with ds,        delaySpeed_ms; ddjustible delay in ms
       di,        delayInput; delay that depends on the input to get
                  the "sneaking" effect (??, not yet used)
  >GGT D=ds,di;
  <ACK C=<command>;
'''

TOK_GGQ     = const(10)
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

TOK_CAL     = const(11)
# Start/stop collecting calibration data. At stop, calibration data is
# processed. Calibration currently only includes servo load
# with st         state, 1=start, 0=stop and process
# >CAL S=st;
# <ACK C=<command>;

TOK_LastInd = const(11)

TOK_NONE    = const(255)
TOK_StrList = ["REM", "VER", "ERR", "ACK", "STA", "XP0",
               "GG0", "GGE", "GGP", "GGT", "GGQ", "CAL"]

_TOK_StrLen             = const(3)
_TOK_MaxPSets           = const(4)
_TOK_MaxValuesPerPSet   = const(32)
_TOK_MinRawMsgLen_bytes = const(10) #8

_TOK_addrTok            = const(0)
_TOK_addrCount          = const(1)
_TOK_addrLen            = const(2) #1
_TOK_addrNPSets         = const(3) #2
_TOK_addrPSetStart      = const(4) #3
_TOK_offsPChar          = const(0)
_TOK_offsNVal           = const(1)
_TOK_offsVals           = const(2)

# For external access ...
TOK_addrPSetStart       = const(_TOK_addrPSetStart)
TOK_offsVals            = const(_TOK_offsVals)
TOK_offsNVal            = const(_TOK_offsNVal)

MSG_Client             = ">"
MSG_Server             = "<"
MSG_EndChr             = ";"
MSG_DataSepChr         = ","

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Message format: ['<' or '>'][int16 array][';']
#
# int16 0   [Token]   Token (as ID)
#       1   [count]  Message number (to sychronize request-reply pairs)
#       2   [len]     Length of complete message in number of int16 values
#       3   [nPSets]  Number of parameter sets (0 ... _TOK_MaxPSets)
#       4   [PChar0]  Type character of 1st parameter set
#       5   [nVal0]   If `nPSets` > 0, number of values for 1st parameter set
#       6   [p0.0]    1st value
#       7   [p0.1]    2nd value
#           ...
#           [PChar1]  Type character of 2nd parameter set, if any
#           [nVal1]   If `nPSets` > 0, number of values for 2nd parameter set
#           [p1.0]
#           ...
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
  MissedExpectedMsgCount = const(9)
  MsgLikelyNotYetInBuf   = const(10)
  NoReply                = const(11)
  Unknown                = const(12)

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

  def __init__(self, typeMsgOut=MSG_Client):
    """ Initialize message content
    """
    self._poll = None
    self._portType = PortType.NONE
    if typeMsgOut in [MSG_Client, MSG_Server]:
      self._typeMsgOut = typeMsgOut
    else:
      self._typeMsgOut = MSG_Client
    self._typeMsgIn = MSG_Client if typeMsgOut == MSG_Server else MSG_Server
    self._count = 0
    self.reset(clearBuf=True)

  def reset(self, token=TOK_NONE, clearBuf=False):
    """ Reset message content
    """
    if clearBuf:
      self._sInBuf = ""
    n = 3 +(2 +_TOK_MaxValuesPerPSet) *_TOK_MaxPSets
    msg = array.array("h", [0] *n)
    msg[_TOK_addrTok] = token
    msg[_TOK_addrCount] = -1
    msg[_TOK_addrLen] = _TOK_addrPSetStart
    msg[_TOK_addrNPSets] = 0
    self._msg = msg
    self._addrPSet = array.array("H", [0]*_TOK_MaxPSets)
    self._nPSetVals = array.array("H", [0]*_TOK_MaxPSets)
    self._lastHexMsgIn = ""
    self._errC = Err.Ok

  @property
  def port_type(self):
    return self._portType

  @property
  def error(self):
    return self._errC

  @property
  def in_buffer_len(self):
    return len(self._sInBuf)

  @property
  def count(self):
    return self._msg[_TOK_addrCount]

  @property
  def token(self):
    return self._msg[_TOK_addrTok]

  @token.setter
  def token(self, val):
    self.errC = Err.Ok
    if val < 0 or val > TOK_LastInd:
      self._msg[_TOK_addrTok] = TOK_NONE
      self._errC = Err.CmdNotRecognized
    else:
      self._msg[_TOK_addrTok] = self._tok = val

  @property
  def msg_as_array(self):
    return self._msg

  def __getitem__(self, iKD):
    i = iKD[0]
    j = iKD[1]
    msg = self._msg
    if i >= 0 and i < msg[_TOK_addrNPSets] and j >= 0 and j < self._nPSetVals[i]:
      return msg[self._addrPSet[i] +_TOK_offsVals +j]
    else:
      return None

  def __setitem__(self, iKD, val):
    i = iKD[0]
    j = iKD[1]
    msg = self._msg
    if i >= 0 and i < msg[_TOK_addrNPSets] and j >= 0 and j < self._nPSetVals[i]:
      self._msg[self._addrPSet[i] +_TOK_offsVals +j] = val

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  def add_data(self, key, data):
    """ Add a parameter key with data
    """
    n = len(data)
    assert n <= _TOK_MaxValuesPerPSet, "Too many values in parameter set"
    i = self._msg[_TOK_addrNPSets]
    assert i < _TOK_MaxPSets, "Too many parameter sets"
    if i == 0:
      p = _TOK_addrPSetStart
    else:
      p = self._addrPSet[i-1] +_TOK_offsVals +self._nPSetVals[i-1]
    self._msg[p +_TOK_offsPChar] = ord(key[0])
    self._msg[p +_TOK_offsNVal] = n
    q = p +_TOK_offsVals
    self._msg[q:q+n] = array.array("h", data)
    self._nPSetVals[i] = n
    self._addrPSet[i] = p
    self._msg[_TOK_addrNPSets] += 1
    self._msg[_TOK_addrLen] += _TOK_offsVals +n

  #@timed_function
  def from_hex_string(self, sHex):
    """ Set message content from hexlified string
    """
    if len(sHex) == 0:
      self._errC = Err.CmdStrIncomplete
    else:
      self._errC = Err.Ok
      msg = array.array("h", binascii.unhexlify(sHex))
      n = msg[_TOK_addrNPSets]
      if n > 0:
        p = _TOK_addrPSetStart
        for iP in range(n):
          self._addrPSet[iP] = p
          self._nPSetVals[iP] = msg[p +_TOK_offsNVal]
          p += _TOK_offsVals +msg[p +_TOK_offsNVal]
      self._msg = msg
    return self._errC

  def to_hex_string(self):
    """ Convert message to hexlified string
    """
    msg = self._msg
    n = msg[_TOK_addrLen]
    return self._typeMsgOut +binascii.hexlify(msg[:n]).decode() +MSG_EndChr

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@micropython.native
  def __repr__(self):
    msg = self._msg
    s = self._typeMsgOut +TOK_StrList[msg[_TOK_addrTok]]
    n = msg[_TOK_addrNPSets]
    if n > 0:
      p = _TOK_addrPSetStart
      for i in range(n):
        s += " " +chr(msg[p +_TOK_offsPChar]) +"="
        m = msg[p +_TOK_offsNVal]
        for j in range(m):
          s += str(msg[p +_TOK_offsVals +j])
          s += "," if j < m-1 else ""
        p += _TOK_offsVals +m
    return s +MSG_EndChr

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  #@timed_function
  def send(self, tout_ms=20, await_reply=True, out_count=None):
    """ Send message as string using the respective serial interface. Checks
        for a reply if `await_reply` is True and returns it, if any, as an
        array (=a message w/o start and end character). `out_count` overwrites
        the out's message `count` field. Accepts a timeout `tout_ms` in [ms].
    """
    self._lastHexMsgIn = ""
    msg = self._msg
    tok = msg[_TOK_addrTok]
    if tok < 0 or tok > TOK_LastInd:
      self._errC = Err.CmdNotRecognized
    else:
      cnt = out_count if not out_count is None else self._count
      msg[_TOK_addrCount] = cnt
      self._count = cnt +1
      #print("send count-to-send", msg[_TOK_addrCount])
      n = msg[_TOK_addrLen]
      s = self._typeMsgOut +binascii.hexlify(msg[:n]).decode() +MSG_EndChr
      self.write(s)
      if await_reply:
        if tout_ms > 0 and self._poll:
          self._poll(tout_ms)
        #self._errC = Err.Ok if self.receive(in_count=cnt) else Err.NoReply
        #print("send before-receive, in_count", cnt)
        self.receive(in_count=cnt)
    return self._lastHexMsgIn

  #@timed_function
  def receive_timed(self, tout_ms=20, in_count=None):
    return self.receive(tout_ms, in_count)

  #@micropython.native
  def receive(self, tout_ms=20, in_count=None):
    """ Read from serial connection and check if a complete message is
        available. If `in_count`is defined, discards all messages with a lower
        count; if received message have a higher count, return an error code
    """
    self._errC = Err.Ok
    self._lastHexMsgIn = ""
    #print("receive any=", self.any())
    if self.any() > 0:
      # Characters are waiting; add them to the buffer
      buf = self._sInBuf +self.readline().decode()
      if len(buf) < _TOK_MinRawMsgLen_bytes:
        # Too few characters for a complete message
        self._sInBuf = buf
        return False

      # May contain a complete message
      tmi = self._typeMsgIn
      tmp = buf.split(tmi)
      n = len(tmp)
      i = 0
      #print("receive start:")
      #print(tmp, i, self._sInBuf)
      while i < n:
        if len(tmp[i]) == 0:
          i += 1
          continue
        if wec := MSG_EndChr in tmp[i]:
          # Contains a complete message
          msg = tmp[i][:-1]
          self.from_hex_string(msg)
          cnt = self._msg[_TOK_addrCount]
          #print("receive msg={0}".format(cnt))
          if in_count is None or in_count == cnt:
            # The message requested is equal to the received (or the caller
            # does not care), return the message
            #print("receive -> success")
            self._lastHexMsgIn = msg
            self._sInBuf = tmi +tmi.join(tmp[i+1:])
            #print(tmp, i, self._sInBuf)
            return True
          if in_count:
            if in_count < cnt:
              # An older message was requested (than the received), return
              # an error but keep the current message in the buffer
              #print("receive msg={0} but expected={1} -> error"
              #      .format(cnt, in_count))
              self._sInBuf = tmi +tmi.join(tmp[i:])
              self._errC = Err.MissedExpectedMsgCount
              #print(tmp, i, self._sInBuf)
              return False
            elif in_count > cnt:
              # A younger message was requested (that the received), look
              # at the next message in the buffer ...
              #print("receive msg={0}, expected={1}, i={2}, n={3} -> i++"
              #      .format(cnt, in_count, i, n))
              i += 1
              #print("received now", tmp, i, self._sInBuf)
              continue

      #print("receive msg not found")
      self._sInBuf = tmi +tmi.join(tmp[i:]) if not wec else ""
      self._errC = Err.MsgLikelyNotYetInBuf
      #print(tmp, i, self._sInBuf)
    return False

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def deinit(self):
    pass

# ----------------------------------------------------------------------------
class RMsgUARTMPy(RMsg):
  """A simple string-based interboard message format using a serial UART
     under MicroPython."""

  def __init__(self, uart, typeMsgOut):
    super().__init__(typeMsgOut)
    self._uart = uart
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

  #@timed_function
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
  def __init__(self, bsp, typeMsgOut):
    super().__init__(typeMsgOut)
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

  def __init__(self, com, baudrate, typeMsgOut, timeout=1.0):
    super().__init__(typeMsgOut)
    self._com = com
    self._baudrate = baudrate
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
