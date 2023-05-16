# Copyright (c) 2023, ProphetLamb <prophet.lamb@gmail.com>
import string
import threading
from pynput import mouse
import typing as t

global HK_MODE_CHOOSE,HK_MODE_LISTEN,canonicalize
HK_REPLAY = "replay"
HK_LISTEN = "listen"

class Recorder():
  def __init__(self) -> None:
    self._mode = None
    self._listener = None
    self._controller = None
    self._controller_thread = None
    self._event_queue = []
    self._on_replay_start = None
    self._on_replay_end = None
    self._on_listen_start = None
    self._on_listen_end = None

  def set_replay_cb(self, start: t.Callable[[object], None], end: t.Callable[[object], None]):
    """Set the callback for when a hotkey is bound.

    Args:
        start (t.Callable[[Recorder], None]): The callback function returning the key event, accepting `self`.
        end (t.Callable[[Recorder], None]): The callback function returning the key event, accepting `self`.
    """
    self._on_replay_start = start
    self._on_replay_end = end

  def set_listen_cb(self, start: t.Callable[[object], None], end: t.Callable[[object], None]):
    """Set the callback for when a hotkey is activated.

    Args:
        start (t.Callable[[Recorder], None]): The callback function accepting `self`.
        end (t.Callable[[Recorder], None]): The callback function accepting `self`.
    """
    self._on_listen_start = start
    self._on_listen_end = end

  def set_mode(self, mode: str):
    """Set the hotkey mode.

    Args:
        mode (str): A string representing the mode to set. One of: 'bind', 'listen', None to disable.

    Raises:
        ValueError: If the mode is not one of the expected values.
    """
    if mode != HK_REPLAY and mode != HK_LISTEN and mode != None:
      raise ValueError("invalid mode, expected one of: 'replay', 'listen', None")
    self._mode = mode
    if mode is None:
      self._stop_global_listener()
      self._stop_global_replay()
    elif mode == HK_LISTEN:
      self._start_global_listener()
    else:
      self._start_global_replay()

  def get_mode(self):
    """Get the current hotkey mode."""
    return self._mode

  def _start_global_listener(self):
    # stop any existing listener
    self._stop_global_listener()
    # start new listener
    self._listener = mouse.Listener(on_click=self._on_global_click)
    self._listener.start()

  def _stop_global_listener(self):
    if self._listener is None:
      return
    self._listener.stop()
    self._listener = None

  def _start_global_replay(self):
    # stop any existing controllers
    self._stop_global_replay()
    # start new controller
    self._controller = mouse.Controller()
    self._controller_thread = threading.Thread(target=self._replay_loop)

  def _stop_global_replay(self):
    if self._controller is None:
      return
    self._controller = None
    self._controller_thread.join()
    self._controller_thread = None

  def _on_global_click(self, x, y, button, pressed):
    event_args = (x, y, button, pressed)
    if self._mode == HK_LISTEN:
      self._event_queue += [event_args]
    return event_args

  def _replay_loop(self):
    for (x, y, button, pressed) in self._event_queue:
      # stop if controller is None
      if self._controller is None:
        break
      # move and press/release
      self._controller.position = (x, y)
      if pressed:
        self._controller.press(button)
      else:
        self._controller.release(button)
