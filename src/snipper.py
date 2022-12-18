#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
from tkinter import *
import typing as t

class Snipper():
  """Allows retrieving a region of the screen using the mouse similar to the snipping tool in windows.

    ## Usage
    ```python
    root = Tk()
    snipper=Snipper(root)
    snipper.set_on_select_cb(lambda region: print(region))
    root.after(1000, snipper.enter_select_mode)
    root.mainloop()
    ```
  """
  def __init__(self, master: Tk):
    self._snip_surface = None
    self.master = master
    self._start_x = None
    self._start_y = None
    self._current_x = None
    self._current_y = None
    self._on_select = None

    # selector overlay
    self.master_screen = Toplevel(master)
    self.master_screen.withdraw()
    self.master_screen.attributes("-transparent", "maroon3")
    self.picture_frame = Frame(self.master_screen, background="maroon3")
    self.picture_frame.pack(fill=BOTH, expand=YES)

  def set_select_cb(self, on_select: t.Callable[[int, int, int, int], None]):
    self._on_select = on_select

  def enter_select_mode(self):
    self.master_screen.deiconify()
    self.master.withdraw()

    self._snip_surface = Canvas(self.picture_frame, cursor="cross", bg="grey11")
    self._snip_surface.pack(fill=BOTH, expand=YES)

    self._snip_surface.bind("<ButtonPress-1>", self._on_select_button_press)
    self._snip_surface.bind("<B1-Motion>", self._on_select_drag)
    self._snip_surface.bind("<ButtonRelease-1>", self._on_select_button_release)

    self.master_screen.attributes('-fullscreen', True)
    self.master_screen.attributes('-alpha', .3)
    self.master_screen.lift()
    self.master_screen.attributes("-topmost", True)
    self.master_screen.bind("<Escape>", self._on_select_cancel)

  def exit_select_mode(self):
    self._snip_surface.destroy()
    self.master_screen.unbind("<Escape>")
    self.master_screen.withdraw()
    self.master.deiconify()

  def _on_select_cancel(self, event):
    self.exit_select_mode()
    return event

  def _on_select_button_release(self, event):
    if self._start_x <= self._current_x and self._start_y <= self._current_y:
      self.set_select(self._start_x, self._start_y, self._current_x - self._start_x, self._current_y - self._start_y)

    elif self._start_x >= self._current_x and self._start_y <= self._current_y:
      self.set_select(self._current_x, self._start_y, self._start_x - self._current_x, self._current_y - self._start_y)

    elif self._start_x <= self._current_x and self._start_y >= self._current_y:
      self.set_select(self._start_x, self._current_y, self._current_x - self._start_x, self._start_y - self._current_y)

    elif self._start_x >= self._current_x and self._start_y >= self._current_y:
      self.set_select(self._current_x, self._current_y, self._start_x - self._current_x, self._start_y - self._current_y)

    self.exit_select_mode()
    return event

  def set_select(self, x1, y1, x2, y2):
    self.select_region = (x1, y1, x2, y2)
    # call the on_select callback
    if self._on_select is not None:
      self._on_select(self.select_region)

  def _on_select_button_press(self, event):
    # save mouse drag start position
    self._start_x = self._snip_surface.canvasx(event.x)
    self._start_y = self._snip_surface.canvasy(event.y)
    self._snip_surface.create_rectangle(0, 0, 1, 1, outline='red', width=3, fill="maroon3")
    return event

  def _on_select_drag(self, event):
    self._current_x, self._current_y = (event.x, event.y)
    # expand rectangle as you drag the mouse
    self._snip_surface.coords(1, self._start_x, self._start_y, self._current_x, self._current_y)
    return event

if __name__ == '__main__':
  # function test
  root = Tk()
  snipper=Snipper(root)
  snipper.set_select_cb(lambda region: print(region))
  root.after(1000, snipper.enter_select_mode)
  root.mainloop()
