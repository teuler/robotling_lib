# ----------------------------------------------------------------------------
# board_feathers2.py
# Hardware specific pin definitions.
#
# The MIT License (MIT)
# Copyright (c) 2021 Thomas Euler
# 2021-04-37, v1
# ----------------------------------------------------------------------------
from micropython import const

__version__ = "0.1.0.0"

# ----------------------------------------------------------------------------
# UnexpectedMaker FeatherS2 (ESP-S2)
# (USB connector up, from the top)
#
# NOTE: For consistency reasons with the FeatherS2 guide, IOxx numbers
# instead of Dxx are given
#
# Left column:
# pylint: disable=bad-whitespace
IO0         = const(0)   # 0
IO17        = const(17)  # 17, A0  (ADC2), DAC 1
IO18        = const(18)  # 18, A1  (ADC2), DAC 2
IO13        = const(13)  # 13, A2  (ADC2), blue LED
IO12        = const(12)  # 12, A3  (ADC2)
IO6         = const(6)   #  6, A4  (ADC1)
IO5         = const(5)   #  5, A5  (ADC1)
IO36        = const(36)  # 36, SPI (SCK)
IO35        = const(35)  # 35, SPI (SDO)
IO37        = const(37)  # 37, SPI (SDI)
IO44        = const(44)  # 44, RX
IO43        = const(43)  # 43, TX

# Right column:
IO11        = const(11)  # 11, A6  (ADC2)
IO10        = const(10)  # 10, A7  (ADC1)
IO7         = const(7)   #  7, A8  (ADC1)
IO3         = const(3)   #  3, A9  (ADC1)
IO1         = const(1)   #  1, A10 (ADC1)
IO38        = const(38)  # 38 
IO33        = const(33)  # 33
IO9         = const(9)   #  9, I2C (SCL)
IO8         = const(8)   #  8, I2C (SDA)

# Alternaternative pins names
A0          = const(17)
A1          = const(18)
A2          = const(13)
A3          = const(12)
A4          = const(6)
A5          = const(5)
A6          = const(11)
A7          = const(10)
A8          = const(7)
A9          = const(3)
A10         = const(1)
SDA         = const(8)  
SCL         = const(9)  
TX          = const(43)  # Serial
RX          = const(44)  # Serial
SDO         = const(35)  # former MOSI
SDI         = const(37)  # former MISO
SCK         = const(36)
DAC1        = const(17)
DAC2        = const(18)
LED         = const(13)  # blue onboard LED

# Internal:
APA102_SCK  = const(45)  # APA102 Dotstar, clock
APA102_DATA = const(40)  # APA102 Dotstar, data
AMB_LT      = const(4)   # Ambient light sensor
LDO2        = const(21)  # LDO2 enable

# pylint: enable=bad-whitespace
# ----------------------------------------------------------------------------
