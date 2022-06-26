# ----------------------------------------------------------------------------
# board_hexapod_0_41_rp2nanoconnect.py
# Pins and devices on `hexapod" board, version 0.4.1 (1=server, 2=client)
#
# The MIT License (MIT)
# Copyright (c) 2020-22 Thomas Euler
# 2020-08-01, v1
# 2020-08-01, v1.1, Board revision (v0.3)
# 2021-01-30, v1.1, Board revision (v0.4), w/ Stemma QT I2C port, fixes
# 2022-01-02, v1.2, w/ rp2040 nano connect instead of TinyPICO
# ----------------------------------------------------------------------------
from micropython import const
import robotling_lib.platform.rp2.board_rp2nanoconnect as board

# pylint: disable=bad-whitespace
# SPI -----------------
SCK        = board.GP18
SDI        = board.GP16
SDO        = board.GP19
CS_ADC     = board.GP17

# I2C -----------------
SCL        = board.GP13
SDA        = board.GP12

# -> Client -----------
# UART 0
UART_CH    = const(0)
TX         = board.GP0
RX         = board.GP1
BAUD       = 230400

# -> Maestro ----------
# UART 1
UART2_CH   = const(1)
TX2        = board.GP4
RX2        = board.GP5
BAUD2      = 115200

# LEDs ----------------
RED_LED    = None
YELLOW_LED = board.GP21
NEOPIX     = board.GP7
DS_CLOCK   = None
DS_DATA    = None
DS_POWER   = None

# Other ---------------
SERVO_FRQ  = 50
BUZZER     = board.GP20

# Power ---------------
ADC_POT    = board.AI1
ADC_BAT    = board.AI0
KEYPAD_POW = None

# pylint: enable=bad-whitespace
# ----------------------------------------------------------------------------
