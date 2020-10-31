# ----------------------------------------------------------------------------
# robotling_base.py
# Definition of a base class `RobotlingBase`, from which classes that capture
# all functions and properties of a specific board
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-09-04, v1
# 2020-10-31, v1.1, use `languageID` instead of `ID`
# ----------------------------------------------------------------------------
import gc
from micropython import const
from robotling_lib.misc.helpers import TimeTracker

import robotling_lib.misc.ansi_color as ansi
from robotling_lib.platform.platform import platform
if platform.languageID == platform.LNG_MICROPYTHON:
  import time
elif platform.languageID == platform.LNG_CIRCUITPYTHON:
  import robotling_lib.platform.circuitpython.time as time
else:
  print(ansi.RED +"ERROR: No matching libraries in `platform`." +ansi.BLACK)

__version__      = "0.1.1.0"

# ----------------------------------------------------------------------------
class RobotlingBase(object):
  """Robotling base class.

  Methods:
  -------
  - connectToWLAN():
    Connect to WLAN if not already connected

  - updateStart(), updateEnd()
    To be called at the beginning and the end of an update routine
  - spin_ms(dur_ms=0, period_ms=-1, callback=None)
    Instead of using a timer that calls `update()` at a fixed frequency (e.g.
    at 20 Hz), one can regularly, calling `spin()` once per main loop and
    everywhere else instead of `time.sleep_ms()`. For details, see there.
  - spin_while_moving(t_spin_ms=50)
    Call spin frequently while waiting for the current move to finish

  - powerDown()
    To be called when the robot shuts down; to be overwritten

  Properties:
  ----------
  - memory         : Returns allocated and free memory as tuple

  Internal methods:
  ----------------
  - _pulseNeoPixel()
    Update pulsing, if enabled
  """
  MIN_UPDATE_PERIOD_MS = const(20)  # Minimal time between update() calls
  APPROX_UPDATE_DUR_MS = const(8)   # Approx. duration of the update/callback
  HEARTBEAT_STEP_SIZE  = const(5)   # Step size for pulsing NeoPixel

  def __init__(self, NeoPixel=False, MCP3208=False):
    """ Initialize spin management
    """
    # Get the current time in seconds
    self._run_duration_s = 0
    self._start_s = time.time()

    # Initialize some variables
    self.ID = platform.GUID
    self.Tele = None
    self._MCP3208 = None
    self._NPx = None

    if MCP3208:
      # Initialize analog sensor driver
      import robotling_lib.driver.mcp3208 as mcp3208
      self._SPI = busio.SPIBus(rb.SPI_FRQ, rb.SCK, rb.MOSI, rb.MISO)
      self._MCP3208 = mcp3208.MCP3208(self._SPI, rb.CS_ADC)

    if NeoPixel:
      # Initialize Neopixel (connector)
      if platform.languageID == platform.LNG_MICROPYTHON:
        from robotling_lib.platform.esp32.neopixel import NeoPixel
      elif platform.languageID == platform.LNG_CIRCUITPYTHON:
        from robotling_lib.platform.m4ex.neopixel import NeoPixel
      self._NPx = NeoPixel(rb.NEOPIX, 1)
      self._NPx0_RGB = bytearray([0]*3)
      self._NPx0_curr = array.array("i", [0,0,0])
      self._NPx0_step = array.array("i", [0,0,0])
      self.NeoPixelRGB = 0
      print("[{0:>12}] {1:35}".format("Neopixel", "ready"))

    # Initialize spin function-related variables
    self._spin_period_ms = 0
    self._spin_t_last_ms = 0
    self._spin_callback = None
    self._spinTracker = TimeTracker()

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def memory(self):
    import gc
    gc.collect()
    return (gc.mem_alloc(), gc.mem_free())

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def powerDown(self):
    """ Record run time
    """
    self._run_duration_s = time.time() -self._start_s

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def updateStart(self):
    """ To be called at the beginning of the update function
    """
    self._spinTracker.reset()
    if self._MCP3208:
      self._MCP3208.update()
    if self._NPx:
      self._pulseNeoPixel()
    '''
    gc.collect()
    '''

  def updateEnd(self):
    """ To be called at the end of the update function
    """
    if self._spin_callback:
      self._spin_callback()
    self._spinTracker.update()

  def spin_ms(self, dur_ms=0, period_ms=-1, callback=None):
    """ If not using a Timer to call `update()` regularly, calling `spin()`
        once per main loop and everywhere else instead of `time.sleep_ms()`
        is an alternative to keep the robotling board updated.
        e.g. "spin(period_ms=50, callback=myfunction)"" is setting it up,
             "spin(100)"" (~sleep for 100 ms) or "spin()" keeps it running.
    """
    if self._spin_period_ms > 0:
      p_ms = self._spin_period_ms
      p_us = p_ms *1000
      d_us = dur_ms *1000

      if dur_ms > 0 and dur_ms < (p_ms -APPROX_UPDATE_DUR_MS):
        time.sleep_ms(int(dur_ms))

      elif dur_ms >= (p_ms -APPROX_UPDATE_DUR_MS):
        # Sleep for given time while updating the board regularily; start by
        # sleeping for the remainder of the time to the next update ...
        t_us  = time.ticks_us()
        dt_ms = time.ticks_diff(time.ticks_ms(), self._spin_t_last_ms)
        if dt_ms > 0 and dt_ms < p_ms:
          time.sleep_ms(dt_ms)

        # Update
        self.update()
        self._spin_t_last_ms = time.ticks_ms()

        # Check if sleep time is left ...
        d_us = d_us -int(time.ticks_diff(time.ticks_us(), t_us))
        if d_us <= 0:
          return

        # ... and if so, pass the remaining time by updating at regular
        # intervals
        while time.ticks_diff(time.ticks_us(), t_us) < (d_us -p_us):
          time.sleep_us(p_us)
          self.update()

        # Remember time of last update
        self._spin_t_last_ms = time.ticks_ms()

      else:
        # No sleep duration given, thus just check if time is up and if so,
        # call update and remember time
        d_ms = time.ticks_diff(time.ticks_ms(), self._spin_t_last_ms)
        if d_ms > self._spin_period_ms:
          self.update()
          self._spin_t_last_ms = time.ticks_ms()

    elif period_ms > 0:
      # Set up spin parameters and return
      self._spin_period_ms = period_ms
      self._spin_callback = callback
      self._spinTracker.reset(period_ms)
      self._spin_t_last_ms = time.ticks_ms()

    else:
      # Spin parameters not setup, therefore just sleep
      time.sleep_ms(dur_ms)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def connectToWLAN(self):
    """ Connect to WLAN if not already connected
    """
    if platform.ID in [platform.ENV_ESP32_UPY, platform.ENV_ESP32_TINYPICO]:
      import network
      from NETWORK import my_ssid, my_wp2_pwd
      if not network.WLAN(network.STA_IF).isconnected():
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
          print('Connecting to network...')
          sta_if.active(True)
          sta_if.connect(my_ssid, my_wp2_pwd)
          while not sta_if.isconnected():
            self.greenLED.on()
            time.sleep(0.05)
            self.greenLED.off()
            time.sleep(0.05)
          print("[{0:>12}] {1}".format("network", sta_if.ifconfig()))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def printReport(self):
    """ Prints a report on memory usage and performance
    """
    used, free = self.memory
    total = free +used
    print("Memory     : {0:.0f}% of {1:.0f}kB heap RAM used."
          .format(used/total*100, total/1024))
    avg_ms = self._spinTracker.meanDuration_ms
    dur_ms = self._spinTracker.period_ms
    print("Performance: spin: {0:6.3f}ms @ {1:.1f}Hz ~{2:.0f}%"
          .format(avg_ms, 1000/dur_ms, avg_ms /dur_ms *100))

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def NeoPixelRGB(self):
    return self._NPx_RGB

  @NeoPixelRGB.setter
  def NeoPixelRGB(self, value):
    """ Set color of NeoPixel at RBL_NEOPIX by assigning RGB values (and
        stop pulsing, if running)
    """
    try:
      rgb = bytearray([value[0], value[1], value[2]])
    except TypeError:
      rgb = bytearray([value]*3)
    self._NPx.set(rgb, 0, True)
    self._NPx0_pulse = False

  def startPulseNeoPixel(self, value):
    """ Set color of NeoPixel at RBL_NEOPIX and enable pulsing
    """
    try:
      rgb = bytearray([value[0], value[1], value[2]])
    except TypeError:
      rgb = bytearray([value]*3)
    if (rgb != self._NPx0_RGB) or not(self._NPx0_pulse):
      # New color and start pulsing
      c = self._NPx0_curr
      s = self._NPx0_step
      c[0] = rgb[0]
      s[0] = int(rgb[0] /self.HEARTBEAT_STEP_SIZE)
      c[1] = rgb[1]
      s[1] = int(rgb[1] /self.HEARTBEAT_STEP_SIZE)
      c[2] = rgb[2]
      s[2] = int(rgb[2] /self.HEARTBEAT_STEP_SIZE)
      self._NPx0_RGB = rgb
      self._NPx.set(rgb, 0, True)
      self._NPx0_pulse = True
      self._NPx0_fact = 1.0

  def dimNeoPixel(self, factor=1.0):
    self._NPx0_fact = max(min(1, factor), 0)

  def _pulseNeoPixel(self):
    """ Update pulsing, if enabled
    """
    if self._NPx0_pulse:
      rgb = self._NPx0_RGB
      for i in range(3):
        self._NPx0_curr[i] += self._NPx0_step[i]
        if self._NPx0_curr[i] > (rgb[i] -self._NPx0_step[i]):
          self._NPx0_step[i] *= -1
        if self._NPx0_curr[i] < abs(self._NPx0_step[i]):
          self._NPx0_step[i] = abs(self._NPx0_step[i])
        if self._NPx0_fact < 1.0:
          self._NPx0_curr[i] = int(self._NPx0_curr[i] *self._NPx0_fact)
      self._NPx.set(self._NPx0_curr, 0, True)
      if not self._DS == None:
        self._DS[random.randint(0, 71)] = self._NPx0_curr
        self._DS.show()

# ----------------------------------------------------------------------------
