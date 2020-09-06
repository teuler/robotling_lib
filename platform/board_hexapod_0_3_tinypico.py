# ----------------------------------------------------------------------------
# board_hexapod_0_3_tinypico.py
# Pins and devices on `hexapod" board, version 0.3
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-08-01, v1
# ----------------------------------------------------------------------------
from micropython import const
import robotling_lib.platform.esp32.board_tinypico as board

# pylint: disable=bad-whitespace
# SPI -----------------
SCK        = board.SCK
MOSI       = board.MOSI
MISO       = board.MISO

# I2C -----------------
SCL        = board.SCL
SDA        = board.SDA

# -> Client -----------
# UART 1
UART_CH    = const(1)
TX         = board.D14
RX         = board.D04
BAUD       = 115200 #38400

# -> Maestro ----------
# UART 2
UART2_CH   = const(2)
TX2        = board.D21
RX2        = board.D22
BAUD2      = 57600

# Other ---------------
DS_CLOCK   = board.DSCL
DS_DATA    = board.DSDT
DS_POWER   = board.DSPW

GREEN_LED  = board.D27
SERVOS_OFF = board.D25
BUZZER     = board.D15
ADC_POT    = board.D32
ADC_BAT    = board.D33
KEYPAD_POW = board.D26

SERVO_FRQ  = 50
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
