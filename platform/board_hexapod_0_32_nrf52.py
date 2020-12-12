# ----------------------------------------------------------------------------
# board_hexapod_0_32_nrf52.py
# Pins and devices on `hexapod' board, version 0.3.2 (1=client)
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-08-01, v1
# ----------------------------------------------------------------------------
from micropython import const
import board

# pylint: disable=bad-whitespace
# SPI -----------------
'''
SCK        = board.SCK
MOSI       = board.MOSI
MISO       = board.MISO
CS_ADC     = board.D33
'''
# I2C -----------------
SCL        = board.SCL
SDA        = board.SDA

# -> Client -----------
# UART 1
UART_CH    = const(1)
TX         = board.TX
RX         = board.RX
'''
D_CLI      = board.D32
'''
BAUD       = 115200

# -> Tera EvoMini -----
# UART 2
UART2_CH   = const(2)
TX2        = board.D5
RX2        = board.A5

# DIO -----------------
'''
DIO0       = board.A0
DIO1       = board.A1
DIO2       = board.D27
DIO3       = board.D21
NEOPIX     = board.D15
'''

# Other ---------------
RED_LED    = board.RED_LED
'''
GREEN_LED  = board.D21
'''
ADC_BAT    = board.BATTERY
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
