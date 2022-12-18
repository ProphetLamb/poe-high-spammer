# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
from pynput import mouse
from tkinter import *
import numpy as np
import random
import typing as t

class Spammer:
  def __init__(self, master: Tk):
    self.master = master
    self._spammer_active = False
    self._mouse_sim = mouse.Controller()
    self._queued_scroll = 0
    self._scroll_listener = None
    self._on_spam = None
    self._count = 0

  def set_spam_cb(self, cb: t.Callable[[np.ndarray, t.List[tuple]], bool]):
    self._on_spam = cb

  def is_active(self) -> bool:
    return self._spammer_active

  def get_count(self) -> int:
    """ returns the number of left mouse clicks that have been sent since the spammer was started """
    return self._count

  def get_queued_count(self) -> int:
    """ returns the number of scroll actions that are queued """
    return self._queued_scroll

  def start(self):
    """ remaps the scroll wheel to the left mouse button
    """
    self.stop() # ensure that the spammer is not already running

    self._spammer_active = True
    self._count = 0
    self._queued_scroll = 0 # reset the scroll queue
    self._scroll_listener = mouse.Listener(on_scroll=self._on_scroll)
    self._scroll_listener.start()
    self._spam_loop()

  def stop(self):
    """ stops the remapping of the scroll wheel to the left mouse button
    """
    self._spammer_active = False
    if self._scroll_listener is not None:
      self._scroll_listener.stop()
      self._scroll_listener = None

  def _spam_loop(self):
    """ consumes the scroll queue and repeats left mouse clicks in random intervals around 4Hz
    """
    if not self._spammer_active:
      return
    self.master.after(140 + random.randrange(0, 110), self._spam_loop)
    rem_scroll = self._queued_scroll - 1
    if rem_scroll >= 0:
      self._queued_scroll = rem_scroll
      self._spam_once()

  def _on_scroll(self, x, y, dx, dy):
    # queue scroll actions
    self._queued_scroll += abs(dx) + abs(dy)

  def _spam_once(self):
    if self._on_spam is None or not self._on_spam():
      self.stop()
    else:
      self._count += 1
      self._mouse_sim.click(mouse.Button.left)
