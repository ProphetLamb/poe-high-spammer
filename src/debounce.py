# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>

from time import time
import typing as t

class Debouncer:
  """ A simple debouncer that calls a callback only if a certain time has passed since the last call.
  """
  def __init__(self, interval_ms: int = 1000):
    self._interval_s = interval_ms / 1000.0
    self._last_call = None

  def is_ready(self) -> bool:
    if self._last_call is None:
      return True
    return time() - self._last_call > self._interval_s

  def call(self, cb: t.Callable) -> t.Optional[any]:
    if self.is_ready():
      self._last_call = time()
      return cb()
    return None


