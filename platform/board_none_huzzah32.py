# ----------------------------------------------------------------------------
# board_none_huzzah32.py
# Pins and devices w/o a `robotling" board
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

# I2C -----------------
SCL        = board.SCL
SDA        = board.SDA

# -> Client -----------
# UART 1
UART_CH    = const(1)
TX         = board.TX
RX         = board.RX
BAUD       = 115200 #38400

# Other ---------------
RED_LED    = board.LED
ADC_BAT    = board.BAT
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
