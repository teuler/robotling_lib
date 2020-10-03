# robotling_lib
["robotling"](https://github.com/teuler/robotling) is a simple circuit board to control small robots, mainly for educational purpose. This repository contains robotling-related hardware and software libraries.

> Note: _Several of the drivers are based on code developed by [Adafruit](https://github.com/adafruit); for details on source, copyright, original authors etc., see information in respective file header._ 

For an overview of some of the supported hardware, see ["Sensoren etc."](https://github.com/teuler/robotling/wiki/Sensoren-etc) (in German).

> Note: _Some of the drivers (e.g. [TeraRanger Evo Mini](https://www.terabee.com/shop/lidar-tof-range-finders/teraranger-evo-mini/), which requires an UART port to access its full functionality) are not compatible to the current robotling board._

## Structure of this repository

```
├───driver                 - Drivers for ICs and break-out modules on the board
├───misc                   - Support functions and classes
├───motors                 - Motor and servo controller classes
├───platform               - Support for different platforms
│   ├───esp32              - For ESP32 based modules, e.g. HUZZAH32, TinyPICO
|   |   └───register       - Register classes (like in CircuitPython)        
│   └───m4ex               - For Adafruit Feather M4 Express
│       └───circuitpython     
│           └───register
├───remote                 - MQTT telemetry, BLE support (ESP32 only) 
└───sensors                - Sensor classes 
```

## List of Classes

Device drivers (`driver`):
- `amg88xx.py` - Class for AMG88XX GRID-Eye IR 8x8 thermal camera driver
- `bno055.py`, `bno055_mpy.mpy` - Class for BNO055 9-DOF IMU fusion breakout
- `dotstar.py` - Class for dotstar FeatherWing
- `drv8835.py` - Class for Pololu dual-channel DC motor driver DRV8835
- `lsm303.py` - Class for LSM303 accelerometer/magnetometer driver
- `lsm9ds0.py` - Class for LSM9DS0 accelerometer/magnetometer/gyroscope driver
- `mcp3208.py` - Class for 8-channel 12-bit SPI A/D converter MCP3208 driver
- `pca9685.py` - Class for PCA9685 16-channel servo driver
- `ssd1327.py` - Class for SSD1327 OLED monochrom display (I2C)


