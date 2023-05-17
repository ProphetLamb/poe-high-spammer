# Copyright (c) 2023, ProphetLamb <prophet.lamb@gmail.com>
from pynput import mouse
from tkinter import *
import numpy as np
import random
import typing as t

class ScrollListener:
  def __init__(self):
    self._scroll_listener = None
    self._on_scroll = None

  def set_scroll_cb(self, cb: t.Callable[[float, float, float, float], None]):
    """Sets the scroll callback.

    Args:
        cb (t.Callable[[object], None]): The function accepting `self`.
    """
    self._on_scroll = cb

  def start(self):
    self._scroll_listener = mouse.Listener(on_scroll=self._on_scroll)
    self._scroll_listener.start()

  def stop(self):
    """ stops the remapping of the scroll wheel to the left mouse button
    """
    if self._scroll_listener is not None:
      self._scroll_listener.stop()
      self._scroll_listener = None

class ScrollController:
  def __init__(self) -> None:
    self._scroll_listener = ScrollListener()
    self._scroll_listener.set_scroll_cb(self._on_scroll)
    self._scroll_action = None
    self._controller_active = False
    self._on_loop = None

  def set_cb(self, cb: t.Callable[[], bool]):
    self._on_loop = cb

  def set_action(self, scroll_action):
    active = self._controller_active
    if active == True:
      self.stop()

    self._scroll_action = scroll_action
    self._scroll_action.set_cb(self._on_loop)

    self.stop()

  def is_active(self) -> bool:
    return self._scroll_action.is_active()

  def get_count(self) -> int:
    """ returns the number of left mouse clicks that have been sent since the spammer was started
    """
    return self._scroll_action.get_count()

  def get_queued_count(self) -> bool:
    """ returns the number of scroll actions that are queued
    """
    return self._scroll_action.get_queued_count()

  def start(self):
    if self._controller_active == True:
      return
    self._controller_active = True
    self._scroll_listener.start()
    self._scroll_action.start()

  def stop(self):
    if self._controller_active == False:
      return
    self._controller_active = False
    self._scroll_listener.stop()
    self._scroll_action.stop()

  def _on_scroll(self, x, y, dx, dy):
    """ callback for the scroll listener
    """
    if self._scroll_action is not None:
      self._scroll_action.loop()
