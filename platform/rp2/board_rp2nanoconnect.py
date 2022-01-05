# ----------------------------------------------------------------------------
# board_rp2nanoconnect.py
# Hardware specific pin definitions.
#
# The MIT License (MIT)
# Copyright (c) 2022 Thomas Euler
# 2022-01-02, v1
# ----------------------------------------------------------------------------
from micropython import const

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
# Arduino rp2040 Nano Connect
# (USB connector down, from the top)
#
# pylint: disable=bad-whitespace
# Left column:
GP6  = const(6)   # D13, I2C1_SDA, SPI0_SCK
                  # +3V3
                  # AREF
GP26 = const(26)  # D14, I2C0_SDA
GP27 = const(27)  # D15, I2C0_SCL
GP28 = const(28)  # D16
GP29 = const(29)  # D17
GP12 = const(12)  # D18, I2C0_SDA, SPI1_RX
GP13 = const(13)  # D19, I2C0_SCL, SPI1_CSn
                  # D20, AI6
                  # D21, AI7
                  # +5V
                  # RESET
                  # gnd
                  # VIN
# Right column:
GP4  = const(4)   # D12, I2C0_SDA, SPI0_RX,  UART1_TX
GP7  = const(7)   # D11, I2C1_SCL, SPI0_TX
GP5  = const(5)   # D10, I2C0_SCL, SPI0_CSn, UART1_RX
GP21 = const(21)  # D9,  I2C0_SCL
GP20 = const(20)  # D8,  I2C0_SDA
GP19 = const(19)  # D7,  I2C1_SCL, SPI0_TX
GP18 = const(18)  # D6,  I2C1_SDA, SPI0_SCK
GP17 = const(17)  # D5,  I2C1_SCL, SPI0_CSn, UART0_RX
GP16 = const(16)  # D4,  I2C1_SCL, SPI0_RX,  UART0_TX
GP15 = const(15)  # D3,  I2C1_SCL, SPI1_TX
GP25 = const(25)  # D2,  I2C1_SCL, SPI0_TX
                  # gnd
                  # RESET
GP1  = const(1)   #      I2C0_SCL, SPI0_CSn, UART0_RX
GP0  = const(0)   #      I2C0_SDA, SPI0_RX,  UART0_TX

# Analog-in
AI0  = const(26)
AI1  = const(27)
AI2  = const(28)
AI3  = const(29)

# Special pins
# n/a
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
