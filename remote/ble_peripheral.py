#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# ble_peripheral.py
# BLESimplePeripheral class
#
# The MIT License (MIT)
# Copyright (c) 2020 Thomas Euler
# 2020-08-16, First version
#
# Adapted from example on:
# https://github.com/micropython/micropython/tree/master/examples/bluetooth
#
# ----------------------------------------------------------------------------
import struct
import bluetooth
from micropython import const
import robotling_lib.remote.ble_helper as bhlp

# pylint: disable=bad-whitespace
__version__   = "0.1.0.0"
CHIP_NAME     = "ble_uart"

_UART_UUID    = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX      = (bluetooth.UUID("6e400002-b5a3-f393-e0a9-e50e24dcca9e"),
                 bluetooth.FLAG_READ | bluetooth.FLAG_NOTIFY,)
_UART_RX      = (bluetooth.UUID("6e400003-b5a3-f393-e0a9-e50e24dcca9e"),
                 bluetooth.FLAG_WRITE | bluetooth.FLAG_WRITE_NO_RESPONSE,)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX,),)

_IRQ_CENTRAL_CONNECT    = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE        = const(3)
# pylint: enable=bad-whitespace

# ----------------------------------------------------------------------------
class BLESimplePeripheral:
  """Class for a simple BLE UART device."""

  def __init__(self, ble, name, max_msg_size=200):
    """ Requires a BLE instance and the name for this peripheral
    """
    self._ble = ble
    self._ble.active(True)
    self._ble.config(rxbuf=max_msg_size)
    self._mac = bhlp.format_mac(self._ble.config("mac"))
    self._ble.irq(self._irq)
    res = self._ble.gatts_register_services((_UART_SERVICE,))
    self._handle_tx = res[0][0]
    self._handle_rx = res[0][1]
    self._ble.gatts_set_buffer(self._handle_tx, max_msg_size)
    self._ble.gatts_set_buffer(self._handle_rx, max_msg_size, True)
    self._connections = set()
    self._rx_buffer = bytearray()
    self._write_callback = None

    self._isReady = True
    self._log("MAC=" +self._mac, "ok" if self._isReady else "NOT FOUND")
    self._payload = bhlp.advertising_payload(name=name, services=[_UART_UUID],)
    self._advertise()

  def deinit(self):
    if self._ble is not None:
      self._advertise(None)
      self._ble.irq(None)
      self._ble.active(False)
      self._isReady == False

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _irq(self, event, data):
    """ Track connections so we can send notifications
    """
    if event == _IRQ_CENTRAL_CONNECT:
      # Add new connection
      conn_handle, _, _, = data
      self._log("#{0} connected".format(conn_handle))
      self._connections.add(conn_handle)

    elif event == _IRQ_CENTRAL_DISCONNECT:
      # Remove connection and start advertising again
      conn_handle, _, _, = data
      self._log("#{0} disconnected".format(conn_handle))
      self._connections.remove(conn_handle)
      self._advertise()

    elif event == _IRQ_GATTS_WRITE:
      # Incoming data received
      conn_handle, value_handle = data
      value = self._ble.gatts_read(value_handle)
      if value_handle == self._handle_rx:
        self._rx_buffer += value
        if self._write_callback:
          self._write_callback(value)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def write(self, data, notify=False):
    """ Send data to all connections
    """
    if notify:
      for conn_handle in self._connections:
        self._ble.gatts_notify(conn_handle, self._handle_tx, data)
    else:
      self._ble.gatts_write(self._handle_tx, data)

  def _advertise(self, interval_us=500000):
    """ Start advertising
    """
    self._log("Started advertising")
    self._ble.gap_advertise(interval_us, adv_data=self._payload)

  def read(self, n=None):
    """ Read data, if available
    """
    if not n:
      n = len(self._rx_buffer)
    res = self._rx_buffer[0:n]
    self._rx_buffer = self._rx_buffer[n:]
    return res

  def on_write(self, callback):
    """ Set callback for incoming data
    """
    self._write_callback = callback

  @property
  def is_connected(self):
    return len(self._connections) > 0

  @property
  def rx_buffer(self):
    return self._rx_buffer

  def _log(self, msg, state=""):
    print("[{0:>12}] {1:35} ({2}): {3}"
          .format(CHIP_NAME, msg, __version__, state))

# ----------------------------------------------------------------------------
