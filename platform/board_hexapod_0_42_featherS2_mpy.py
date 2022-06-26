# ----------------------------------------------------------------------------
# board_hexapod_0_32_featherS2_mpy.py
# Pins and devices on `hexapod' board, version 0.3.2 (1=client)
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-11-15, v1
# ----------------------------------------------------------------------------
from micropython import const
import robotling_lib.platform.esp32.board_feathers2 as board

# pylint: disable=bad-whitespace
# SPI -----------------
SCK        = board.SCK
SDO        = board.SDO
SDI        = board.SDI
CS_ADC     = board.IO3

# I2C -----------------
SCL        = board.SCL
SDA        = board.SDA

# -> Client -----------
# UART 1
UART_CH    = const(1)
TX         = board.TX
RX         = board.RX
D_CLI      = board.IO38
BAUD       = 230400

# -> Tera EvoMini -----
# UART 2
UART2_CH   = const(2)
TX2        = board.IO33
RX2        = board.IO5

# DIO -----------------
DIO0       = board.IO17
DIO1       = board.IO18
DIO2       = board.IO7
#DIO3      = board.IO6
NEOPIX     = board.A10

# LEDs ----------------
BLUE_LED   = board.LED
GREEN_LED  = board.IO6
DS_CLOCK   = board.APA102_SCK
DS_DATA    = board.APA102_DATA
DS_POWER   = None

# Power ---------------
ADC_BAT    = None

# pylint: enable=bad-whitespace
# ----------------------------------------------------------------------------
