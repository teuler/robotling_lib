# ----------------------------------------------------------------------------
# board_hexapod_0_31_tinypico.py
# Pins and devices on `hexapod" board, version 0.3.1 (1=server)
#
# The MIT License (MIT)
# Copyright (c) 2020-21 Thomas Euler
# 2020-08-01, v1
# 2020-08-01, v1.1, Board revision (v0.3)
# 2021-01-30, v1.1, Board revision (v0.4), w/ Stemma QT I2C port, fixes
# ----------------------------------------------------------------------------
from micropython import const
import robotling_lib.platform.esp32.board_tinypico as board

# pylint: disable=bad-whitespace
# SPI -----------------
SCK        = board.SCK
SDI        = board.SDI
SDO        = board.SDO
CS_ADC     = board.D05

# I2C -----------------
SCL        = board.D25
SDA        = board.D26

# -> Client -----------
# UART 1
UART_CH    = const(1)
TX         = board.D14
RX         = board.D04
BAUD       = 230400

# -> Maestro ----------
# UART 2
UART2_CH   = const(2)
TX2        = board.D21
RX2        = board.D22
BAUD2      = 115200 #115200, 230400

# LEDs ----------------
RED_LED    = None
YELLOW_LED = board.D27
DS_CLOCK   = board.APA102_SCK
DS_DATA    = board.APA102_DATA
DS_POWER   = board.APA102_PWR

# Other ---------------
SERVO_FRQ  = 50
BUZZER     = board.D15

# Power ---------------
ADC_POT    = board.D32
ADC_BAT    = board.D33
KEYPAD_POW = board.D26

# pylint: enable=bad-whitespace
# ----------------------------------------------------------------------------
