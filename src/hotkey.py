# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
import string
from pynput import keyboard
import typing as t

global HK_MODE_CHOOSE,HK_MODE_LISTEN,canonicalize
HK_BIND = "bind"
HK_LISTEN = "listen"

def canonicalize(key: t.Union[keyboard.Key, keyboard.KeyCode, None]) -> str:
  """Get the canonical string representation of a key.
  """
  if isinstance(key, keyboard.KeyCode) and key.char is not None and key.char in string.ascii_letters:
      return key.char
  elif isinstance(key, keyboard.Key) and key.name is not None:
      return key.name
  else:
      return '<unknown>'

class Hotkey():
  """A class for binding and listening to global hotkeys."""
  def __init__(self):
    self.bound_key = None
    self._mode = None
    self._listener = None
    self._on_bind = None
    self._on_activate = None
    self._inter_bind_id = None

  def set_bind_cb(self, cb: t.Callable[[object], object]):
    """Set the callback for when a hotkey is bound.

    Args:
        cb (t.Callable[[GlobalHotkey, object], object]): The callback function returning the key event, accepting `self` and the key event.
    """
    self._on_bind = cb

  def set_activate_cb(self, cb: t.Callable[[object], None]):
    """Set the callback for when a hotkey is activated.

    Args:
        cb (t.Callable[[GlobalHotkey, object], None]): The callback function accepting `self` and the key event.
    """
    self._on_activate = cb

  def set_mode(self, mode: str):
    """Set the hotkey mode.

    Args:
        mode (str): A string representing the mode to set. One of: 'bind', 'listen', None to disable.

    Raises:
        ValueError: If the mode is not one of the expected values.
    """
    if mode != HK_BIND and mode != HK_LISTEN and mode != None:
      raise ValueError("invalid mode, expected one of: 'bind', 'listen', None")
    self._mode = mode
    if mode is None:
      self._stop_global_listener()
    else:
      self._start_global_listener()

  def get_mode(self):
    """Get the current hotkey mode."""
    return self._mode

  def _start_global_listener(self):
    # stop any existing listener
    self._stop_global_listener()
    # start new listener
    self._listener = keyboard.Listener(on_press=self._on_global_press)
    self._listener.start()

  def _stop_global_listener(self):
    if self._listener is None:
      return
    self._listener.stop()
    self._listener = None

  def _on_global_press(self, key):
    if self._mode == HK_BIND:
      return self._on_bind_press(key)
    elif self._mode == HK_LISTEN:
      return self._on_listen_press(key)
    return key

  def _on_listen_press(self, key):
    if self.bound_key is None:
      return key
    if self.bound_key == key:
      if self._on_activate is not None:
        self._on_activate(key)
    return key

  def _on_bind_press(self, key):
    if self._on_bind is None:
      self.bound_key = key
    else:
      self.bound_key=self._on_bind(key)
    return key

