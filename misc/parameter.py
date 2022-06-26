#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# parameter.py
# Class capsulating a scalar or vector with automatic limit checking and
# blending
#
# The MIT License (MIT)
# Copyright (c) 2020-21 Thomas Euler
# 2020-05-18, First version
# 2021-06-07, For efficiency, separate versions for scalars and vectors
#
# ----------------------------------------------------------------------------
try:
  ModuleNotFoundError
except NameError:
  ModuleNotFoundError = ImportError
try:
  # Micropython imports
  from ulab import numpy as np
  from robotling_lib.misc.helpers import timed_function
  MICROPYTHON = True
except ModuleNotFoundError:
  # Standard Python imports
  import numpy as np
  MICROPYTHON = False

# ----------------------------------------------------------------------------
class ParameterBase(object):
  """ Base class for parameter objects that ncapsulates a skalar or vector
      parameters and makes sure that it stays within a given range. Also, if
      requested, enables smooth blending between current and target value.
  """
  def __init__(self, lim=0, max_steps=0, unit="-"):
    self._lim = lim
    self._dim = 0
    self._nInc = 0
    self._maxStep = 0
    self._unit = unit
    self._maxStep = max_steps

  def __len__(self):
    return self._dim

  #@timed_function
  def update(self):
    if self._nInc > 0:
      self._val = self._val +self._inc
      self._nInc -= 1

# ----------------------------------------------------------------------------
class Parameter(ParameterBase):
  """ Encapsulates a skalar parameter
  """
  def __init__(self, val: float, _minmax, lim=0, max_steps=0, unit="-"):
    super().__init__(lim, max_steps, unit)
    self._min = _minmax[0]
    self._max = _minmax[1]
    self._target = 0
    self._inc = 0
    self._dim = 1
    self._val = 0
    self._set_val(val)

  def __str__(self):
    _sval = "{0},".format(self._val)
    _smin = "{0},".format(self._min)
    _smax = "{0},".format(self._max)
    return "{0} {1} ({2} ... {3})".format(_sval, self._unit, _smin, _smax)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _get_val(self):
    return self._val

  #@timed_function
  def _set_val(self, val):
    if val is None:
      return
    else:
      self._target = min(max(val, self._min), self._max)
      if self._maxStep == 0:
        self._val = self._target
      else:
        self._nInc = self._maxStep
        self._inc = (self._target -self._val) /self._maxStep

  val = property(_get_val, _set_val)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def x(self):
    return self._val

# ----------------------------------------------------------------------------
class Parameters(ParameterBase):
  """ Encapsulates a vector parameter
  """
  def __init__(self, val: list, _minmax, lim=0, max_steps=0, unit="-"):
    super().__init__(lim, max_steps, unit)

    # Convert into np.array
    self._min = np.array(_minmax[0])
    self._max = np.array(_minmax[1])
    _val = np.array(val)
    n = len(_val)
    if n != len(self._min) or n != len(self._max):
      raise ValueError("Parameters are not consistent")

    # Initialize other variables
    self._target = np.zeros(n)
    self._inc = np.zeros(n)
    self._val = np.zeros(n)
    self._dim = n
    self._set_val(_val)

  def __str__(self):
    _sval = ""
    _smin = ""
    _smax = ""
    for i in range(self._dim):
      _sval += "{0},".format(self._val[i])
      _smin += "{0},".format(self._min[i])
      _smax += "{0},".format(self._max[i])
    return "{0} {1} ({2} ... {3})".format(_sval[:-1], self._unit,
                                          _smin[:-1], _smax[:-1])

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  def _get_val(self):
    return self._val

  #@timed_function
  def _set_val(self, val):
    if val is None:
      return
    else:
      self._target = np.clip(np.array(val), self._min, self._max)
      if self._maxStep == 0:
        self._val = self._target
      else:
        self._nInc = self._maxStep
        self._inc = (self._target -self._val) /self._maxStep

  val = property(_get_val, _set_val)

  # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
  @property
  def x(self):
    return self._val[0]

  @property
  def y(self):
    assert self._dim >= 2, "Dimension out of range"
    return self._val[1]

  @property
  def z(self):
    assert self._dim >= 3, "Dimension out of range"
    return self._val[2]

# ----------------------------------------------------------------------------
