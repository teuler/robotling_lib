# ----------------------------------------------------------------------------
# board_robotling_1_3_sam51.py
# Pins and devices on `robotling" board, version 1.3
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-08-01, v1
# ----------------------------------------------------------------------------
import board

# pylint: disable=bad-whitespace
SCK        = board.SCK
MOSI       = board.MOSI
MISO       = board.MISO
CS_ADC     = board.A5

SCL        = board.SCL
SDA        = board.SDA

A_ENAB     = board.A3
# The M4 express feather does not allow PWM with pin A0, therefore to use
# robotling boards <= v1.2 requires to solder a bridge between the pins A0
# and A3.
A_PHASE    = board.D5
B_ENAB     = board.D4
B_PHASE    = board.A1

ENAB_5V    = board.RX
RED_LED    = board.D13

ADC_BAT    = board.VOLTAGE_MONITOR

NEOPIX     = board.NEOPIXEL
DIO0       = board.D11
DIO1       = board.D13
DIO2       = board.D10
DIO3       = board.D6

# The M4 allows for different frequencies for PWM channels; `MOTOR_A_CH`
# and `MOTOR_B_CH` are -1 because the RMT feature of the ESP32 is not
# available not nescessary here
SERVO_FRQ  = 50
MOTOR_FRQ  = 150
MOTOR_A_CH = -1
MOTOR_B_CH = -1
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
