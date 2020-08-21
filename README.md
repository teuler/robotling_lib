# robotling_lib
["robotling"](https://github.com/teuler/robotling) is a simple circuit board to control small robots, mainly for educational purpose. This repository contains robotling-related hardware and software libraries.

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
