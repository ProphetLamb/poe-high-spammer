# Copyright (c) 2023, ProphetLamb <prophet.lamb@gmail.com>
import random
import threading
import time
from pynput import mouse
import typing as t

class Recorder:
  def __init__(self):
    self._record_active = False
    self._listener = mouse.Listener(on_click=self._on_record)
    self._on_replay = None
    self._event_queue = []

  def set_cb(self, cb: t.Callable[[], bool]):
    self._on_replay = cb

  def is_active(self) -> bool:
    return self._record_active

  def loop(self):
    """ queue scroll actions
    """
    pass

  def events(self):
    return self._event_queue

  def _on_record(self, x, y, button, pressed):
    self._event_queue.append((x, y, button, pressed))

  def get_count(self) -> int:
    """ returns the number of left mouse clicks that have been sent since the spammer was started
    """
    return 0

  def get_queued_count(self) -> bool:
    """ returns the number of scroll actions that are queued
    """
    return False

  def start(self):
    """ remaps the scroll wheel to the left mouse button
    """
    self.stop() # ensure that the spammer is not already running

    self._record_active = True
    self._event_queue = []
    self._listener.start()

  def stop(self):
    """ stops the remapping of the scroll wheel to the left mouse button
    """
    self._record_active = False
    self._listener.stop()

class Replay:
  def __init__(self):
    self._replay_active = False
    self._mouse_sim = mouse.Controller()
    self._queued_scroll = False
    self._on_replay = None
    self._count = 0
    self._event_queue = []
    self._event_position = 0
    self._loop_thread = None

  def set_cb(self, cb: t.Callable[[], bool]):
    self._on_replay = cb

  def set_events(self, events: list):
    self._event_queue = events

  def is_active(self) -> bool:
    return self._replay_active

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

    self._replay_active = True
    self._count = 0
    self._queued_scroll = False # reset the scroll queue
    self._loop_thread = threading.Thread(target=self._replay_loop)
    self._loop_thread.start()

  def stop(self):
    """ stops the remapping of the scroll wheel to the left mouse button
    """
    self._replay_active = False
    self._loop_thread = None

  def _replay_loop(self):
    while self._replay_active:
      time.sleep(0.14 + random.random() * 0.02)
      replay_queued  = self._queued_scroll
      self._queued_scroll = False
      if replay_queued == True:
        self._replay_one()

  def _replay_one(self):
    if self._on_replay is None or not self._on_replay():
      self.stop()
    else:
      self._count += 1

      event_position = self._event_position % len(self._event_queue)
      self._event_position = event_position + 1

      (x, y, button, pressed) = self._event_queue[event_position]
      self._mouse_sim.position = (x, y)
      if pressed:
        self._mouse_sim.press(button)
      else:
        self._mouse_sim.release(button)
