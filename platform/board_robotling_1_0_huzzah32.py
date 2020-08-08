# ----------------------------------------------------------------------------
# board_robotling_1_0_huzzah32.py
# Pins and devices on `robotling" board, version 1.0
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-08-01, v1
# ----------------------------------------------------------------------------
from micropython import const
import robotling_lib.platform.esp32.board_huzzah32 as board

# pylint: disable=bad-whitespace
# SPI -----------------
SCK        = board.SCK
MOSI       = board.MOSI
MISO       = board.MISO
CS_ADC     = board.D4

# I2C -----------------
SCL        = board.SCL
SDA        = board.SDA

# UART  ---------------
TX         = board.TX
RX         = board.RX
BAUD       = 38400

# DC Motors -----------
A_ENAB     = board.D26
A_PHASE    = board.D14
B_ENAB     = board.D21
B_PHASE    = board.D25

# DIO -----------------
NEOPIX     = board.D15      # Connect Neopixel to DIO #0
DIO0       = board.D27
DIO1       = board.LED
DIO2       = board.D33
DIO3       = board.D15

# Other ---------------
ENAB_5V    = board.D16
RED_LED    = board.LED
ADC_BAT    = board.BAT

# Note 1: The ESP32 MicroPython port currently supports only one frequency
# for all PWM objects. Servos usually expect 50 Hz, but to run the DC motors
# somewhat smoother, a higher frequency can be tested
# Note 2: DIO uses now the RMT feature of the ESP32, which offers an
# alternative to the standard PWM with more flexible frequencies
SERVO_FRQ  = 50 #250
MOTOR_FRQ  = SERVO_FRQ
MOTOR_A_CH = 0
MOTOR_B_CH = 1
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
