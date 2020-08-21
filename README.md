# robotling_lib
["robotling"](https://github.com/teuler/robotling) is a simple circuit board to control small robots, mainly for educational purpose. This repository contains robotling-related hardware and software libraries.

For an overview of some of the supported hardware, see ["Sensoren etc."](https://github.com/teuler/robotling/wiki/Sensoren-etc) (in German).

> Note: _Some of the drivers (e.g. [TeraRanger Evo Mini](https://www.terabee.com/shop/lidar-tof-range-finders/teraranger-evo-mini/), which requires an UART port to access its full functionality) are not compatible to the current robotling board._

## Repository-Struktur 

```
├───driver                 - Treiber für ICs und Module auf der Platine 
├───misc                   - Hilfsfunktionen und -Klassen
├───motors                 - Motor- und Servokontroller-Klassen
├───platform               - Klassen für Plattformunabhängigkeit
│   ├───esp32              - für ESP32 based modules, e.g. HUZZAH32, TinyPICO
|   |   └───register       - Register-Klassen (wie in CircuitPython)        
│   └───m4ex               - für Adafruit Feather M4 Express
│       └───circuitpython     
│           └───register
├───remote                 - MQTT-Telemetry, BLE-Unterstützung (ESP32) 
└───sensors                - Sensor-Klassen 
```
