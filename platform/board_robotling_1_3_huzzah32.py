# ----------------------------------------------------------------------------
# board_robotling_1_3_huzzah32.py
# Pins and devices on `robotling" board, version 1.3
#
# The MIT License (MIT)
# Copyright (c) 2020-21 Thomas Euler
# 2020-08-01, v1
# 2021-09-23, v1.1, MISO -> SDI, MOSI -> SDO
# ----------------------------------------------------------------------------
from micropython import const
import robotling_lib.platform.esp32.board_huzzah32 as board

# pylint: disable=bad-whitespace
# SPI -----------------
SCK        = board.SCK
SDO        = board.SDO
SDI        = board.SDI
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
NEOPIX     = board.D15      # -> Neopixel connector
DIO0       = board.D27
DIO1       = board.LED
DIO2       = board.D33
DIO3       = board.D32

# Other ---------------
ENAB_5V    = board.D16
RED_LED    = board.LED
ADC_BAT    = board.BAT
DS_CLOCK   = None

# Note 1: The ESP32 MicroPython port currently supports only one frequency
# for all PWM objects. Servos usually expect 50 Hz, but to run the DC motors
# somewhat smoother, a higher frequency can be tested
# Note 2: DIO uses now the RMT feature of the ESP32, which offers an
# alternative to the standard PWM with more flexible frequencies
# Note 3: Somehow the behaviour of RMT channels has changed sometime early
# 2020; not sure what the problem is. For now, fall back to "normal" PWM
SERVO_FRQ  = 50 # 250
MOTOR_FRQ  = SERVO_FRQ
MOTOR_A_CH = -1 # 0, if RMT channels are used
MOTOR_B_CH = -1 # 1, if TMT channels are used
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
