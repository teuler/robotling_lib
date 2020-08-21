# robotling_lib
["robotling"](https://github.com/teuler/robotling) is a simple circuit board to control small robots, mainly for educational purpose. This repository contains robotling-related hardware and software libraries.

For an overview of some of the supported hardware, see ["Sensoren etc."](https://github.com/teuler/robotling/wiki/Sensoren-etc) (in German).

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
