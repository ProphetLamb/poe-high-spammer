#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
from oir import get_cross_kernel, masked_screenshot, measure_bright_box
from pynput import mouse
from tkinter import *
import numpy as np
import random
import typing as t

class Spammer:
  def __init__(self, master: Tk):
    self.master = master
    self.select_region = None
    self.cross_kernel = get_cross_kernel(5, 3)
    self.select_threshold = None
    self._spammer_active = False
    self._mouse_sim = mouse.Controller()
    self._queued_scroll = 0
    self._scroll_listener = None
    self._on_spam = None

  def set_on_spam_cb(self, cb: t.Callable[[np.ndarray, t.List[tuple]], None]):
    self._on_spam = cb

  def is_active(self) -> bool:
    return self._spammer_active

  def start(self):
    """ remaps the scroll wheel to the left mouse button
    """
    self.stop() # ensure that the spammer is not already running

    self._spammer_active = True
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
    # check whether the selected region exceeds the threshold
    img = masked_screenshot(self.select_region, self.cross_kernel)
    area,bboxes = measure_bright_box(img)
    # invoke the callback
    if self._on_spam is not None:
      self._on_spam(img, bboxes)
    # check whether the selected region exceeds the threshold ...
    if area > self.select_threshold:
      # ... and exit the spam mode if so
      self.exit_spam_mode()
    else:
      # ... otherwise continue to check
      self._mouse_sim.click(mouse.Button.left)

if __name__ == '__main__':
  # function test
  root = Tk()
  spammer=Spammer(root)
  spammer.select_region = (0, 0, 100, 100)
  spammer.select_threshold = 1000
  spammer.set_on_spam_cb(lambda img, bboxes: print(img.shape, bboxes))
  root.after(1000, spammer.start)
  root.mainloop()
