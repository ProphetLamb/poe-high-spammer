# Copyright (c) 2023, ProphetLamb <prophet.lamb@gmail.com>
import threading
import time
from pynput import mouse
import random
import typing as t

class Spammer:
  def __init__(self):
    self._spammer_active = False
    self._mouse_sim = mouse.Controller()
    self._queued_scroll = False
    self._on_spam = None
    self._count = 0
    self._loop_thread = None

  def set_cb(self, cb: t.Callable[[], bool]):
    self._on_spam = cb

  def is_active(self) -> bool:
    return self._spammer_active

  def loop(self):
    """ queue scroll actions
    """
    self._queued_scroll = True

  def get_count(self) -> int:
    """ returns the number of left mouse clicks that have been sent since the spammer was started
    """
    return self._count

  def get_queued_count(self) -> bool:
    """ returns the number of scroll actions that are queued
    """
    return self._queued_scroll

  def start(self):
    """ remaps the scroll wheel to the left mouse button
    """
    self.stop() # ensure that the spammer is not already running

    self._spammer_active = True
    self._count = 0
    self._queued_scroll = False # reset the scroll queue
    self._loop_thread = threading.Thread(target=self._spam_loop)
    self._loop_thread.start()

  def stop(self):
    """ stops the remapping of the scroll wheel to the left mouse button
    """
    self._spammer_active = False
    self._loop_thread = None

  def _spam_loop(self):
    """ consumes the scroll queue and repeats left mouse clicks in random intervals around 4Hz
    """
    while self._spammer_active:
      time.sleep(0.14 + random.random() * 0.02)
      queued_scroll = self._queued_scroll
      self._queued_scroll = False
      if queued_scroll == True:
        self._spam_once()

  def _spam_once(self):
    if self._on_spam is None or not self._on_spam():
      self.stop()
    else:
      self._count += 1
      self._mouse_sim.click(mouse.Button.left)
