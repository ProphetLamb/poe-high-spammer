#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
from tkinter import *
from pynput import keyboard, mouse
import random
from PIL import Image, ImageTk
from oir import masked_screenshot, measure_bright_box, get_cross_kernel, render_bboxes, smart_resize
import numpy as np
import typing as t

from snipper import Snipper

class Application():
  def __init__(self, master: Tk):
    self.master = master
    self.select_region = None
    self.select_threshold = None
    self.hotkey_keycode = None
    self.hotkey_listener = None
    self.spammer_active = False
    self.scroll_listener = None
    self.queued_scroll = 0
    self.mouse_sim = mouse.Controller()
    self.cross_kernel = get_cross_kernel(5)

    # snipper
    self.snipper = Snipper(master)
    self.snipper.set_on_select_cb(self.set_select)

    width, height = 400, 600

    master.resizable(width=False, height=False)
    master.geometry('{}x{}+200+200'.format(width, height))
    master.title('PoE High Spammer')
    master.iconbitmap("./img/logo.ico")

    banner = Image.open("./img/banner.png")
    banner = smart_resize(banner, width = width)
    banner_wd = ImageTk.PhotoImage(banner)
    lbl=Label(master, image=banner_wd)
    lbl.image = banner_wd
    lbl.pack()

    # menu frame
    self.menu_frame = Frame(master, bg="white")
    self.menu_frame.pack(side=TOP, fill=X)

    # selection
    Label(self.menu_frame, text="selection").pack(side=TOP, fill=X)
    # selection ui
    select = Frame(self.menu_frame, height=5, bg="white", padx=5, pady=5)
    select.pack(side=TOP, fill=X)
    Label(select, text="select area", bg="white").pack(side=LEFT, fill=Y)
    self.select_btn = Button(select, command=self.enter_select_mode, text="region")
    self.select_btn.pack(side=RIGHT, fill=Y)
    self.select_lbl = Label(select, text="none", bg="white", fg="red")
    self.select_lbl.pack(side=RIGHT, fill=Y)
    # selection threshold
    threshold = Frame(self.menu_frame, height=5, bg="white", padx=5, pady=5)
    threshold.pack(side=TOP, fill=X)
    Label(threshold, text="area threshold", bg="white").pack(side=LEFT, fill=Y)
    # numeric threshold input which sets self.select_threshold
    self.threshold_entry = Entry(threshold, width=5)
    self.threshold_entry.pack(side=RIGHT, fill=Y)
    self.threshold_entry.insert(0, "300")
    self.threshold_entry.bind("<Tab>", self.on_threshold_change)
    self.threshold_entry.bind("<FocusOut>", self.on_threshold_change)

    # spammer
    Label(self.menu_frame, text="spammer").pack(side=TOP, fill=X)
    # hotkey
    hotkey = Frame(self.menu_frame, height=5, bg="white", padx=5, pady=5)
    hotkey.pack(side=TOP, fill=X)
    Label(hotkey, text="hotkey", bg="white").pack(side=LEFT, fill=Y)
    self.hotkey_edit_btn = Button(hotkey, command=self.enter_hotkey_mode, text="edit")
    self.hotkey_edit_btn.pack(side=RIGHT, fill=Y)
    self.hotkey_edit_label = Label(hotkey, text="none", bg="white", fg="red")
    self.hotkey_edit_label.pack(side=RIGHT, fill=Y)
    # toggle
    spammer = Frame(self.menu_frame, height=5, bg="white", padx=5, pady=5)
    spammer.pack(side=TOP, fill=X)
    Label(spammer, text="spammer", bg="white").pack(side=LEFT, fill=Y)
    self.spammer_lbl = Label(spammer, text="inactive", fg="red", bg="white")
    self.spammer_lbl.pack(side=RIGHT, fill=Y)

    # preview
    Label(self.menu_frame, text="preview", bg="black", fg="white").pack(side=TOP, fill=X)
    self.preview_lbl = Label(self.menu_frame, bg="black")
    self.preview_lbl.pack(side=TOP, fill=BOTH, expand=YES)

    # copyright
    Label(master, text="Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>").pack(side="bottom", fill=X)

  # -----------------------------------------------------------------------------
  # REGION SELECTION
  # -----------------------------------------------------------------------------

  def enter_select_mode(self):
    self.snipper.enter_select_mode()

  def set_select(self, region: t.Tuple[int, int, int, int]):
    self.select_region = region
    img = masked_screenshot(self.select_region, self.cross_kernel)
    box_area,bboxes = measure_bright_box(img)

    self.update_select_lbl(img, box_area)
    self.update_preview_lbl(img, bboxes)
    self.update_threshold(box_area)

  def update_threshold(self, box_area: float):
    # use 90% of the area rounded down to a multiple of 100 to avoid false positives
    thres = int(box_area * .95)
    self.threshold_entry.delete(0, END)
    self.threshold_entry.insert(0, str(thres))
    self.on_threshold_change(None)

  def update_select_lbl(self, img: np.ndarray, box_area: float):
    img_area = pow(img.shape[0] * img.shape[1],.5)
    fill_ratio = box_area / float(img_area)

    self.select_lbl["text"] = "{}found {}px in {}px ({:2.2f}%)".format(
      "" if fill_ratio > .75 else "LOW CERTAINTY ",
      int(box_area),
      int(img_area),
      fill_ratio * 100)
    if fill_ratio > .75:
      self.select_lbl["fg"] = "black"
    else:
      self.select_lbl["fg"] = "red"

  def update_preview_lbl(self, img: np.ndarray, bboxes: t.List[tuple]):
    img = render_bboxes(img, bboxes)
    img = Image.fromarray(img)
    # fix height to 250px
    img = smart_resize(img, height=250)
    img_wg = ImageTk.PhotoImage(img)
    self.preview_lbl.configure(image=img_wg)
    self.preview_lbl.image = img_wg

  # -----------------------------------------------------------------------------
  # AREA THRESHOLD
  # -----------------------------------------------------------------------------

  def on_threshold_change(self, event):
    self.select_threshold = int(self.threshold_entry.get())
    return event

  # -----------------------------------------------------------------------------
  # HOTKEY BINDING
  # -----------------------------------------------------------------------------

  def enter_hotkey_mode(self):
    self.hotkey_edit_btn["text"] = "stop"
    self.hotkey_edit_btn["command"] = self.exit_hotkey_mode
    self.hotkey_edit_btn.pack(side=RIGHT, fill=Y)
    self.master.bind("<Key>", self.on_hotkey_press)
    # stop listening to the hotkey
    if self.hotkey_listener is not None:
      self.hotkey_listener.stop()
      self.hotkey_listener = None

  def exit_hotkey_mode(self):
    self.hotkey_edit_btn["text"] = "edit"
    self.hotkey_edit_btn["command"] = self.enter_hotkey_mode
    self.hotkey_edit_btn.pack(side=RIGHT, fill=Y)
    self.master.unbind("<Key>")
    # start listening to the hotkey
    self.hotkey_listener = keyboard.Listener(on_press=self.on_spammer_triggered)
    self.hotkey_listener.start()

  def on_hotkey_press(self, event):
    # unbind previous from master
    self.hotkey_keycode = event.keycode
    self.hotkey_edit_label["text"] = event.keysym
    self.hotkey_edit_label["fg"] = "black"
    return event

  # -----------------------------------------------------------------------------
  # SPAMMER TOGGLE
  # -----------------------------------------------------------------------------

  def on_spammer_triggered(self, event):
    if not hasattr(event, "vk"):
      return self.on_spammer_triggered(event.value)
    if self.hotkey_keycode == event.vk:
      if self.spammer_active:
        self.exit_spam_mode()
      else:
        self.enter_spam_mode()
    return event

  def enter_spam_mode(self):
    self.spammer_lbl["text"] = "active"
    self.spammer_lbl["fg"] = "green"
    # active the spammer
    self.spammer_active = True
    self.begin_spam_legal()

  def exit_spam_mode(self):
    self.spammer_lbl["text"] = "inactive"
    self.spammer_lbl["fg"] = "red"
    # deactivate the spammer
    self.spammer_active = False
    self.stop_spam_legal()

  # -----------------------------------------------------------------------------
  # LEGAL SPAMMING
  # -----------------------------------------------------------------------------

  def begin_spam_legal(self):
    """ remaps the scroll wheel to the left mouse button
    """
    self.queued_scroll = 0 # reset the scroll queue
    self.scroll_listener = mouse.Listener(on_scroll=self.on_scroll)
    self.scroll_listener.start()
    self.spam_legal_loop()

  def stop_spam_legal(self):
    """ stops the remapping of the scroll wheel to the left mouse button
    """
    if self.scroll_listener is not None:
      self.scroll_listener.stop()
      self.scroll_listener = None

  def spam_legal_loop(self):
    """ consumes the scroll queue and repeats left mouse clicks in random intervals around 4Hz
    """
    if not self.spammer_active:
      return
    self.master.after(140 + random.randrange(0, 110), self.spam_legal_loop)
    rem_scroll = self.queued_scroll - 1
    if rem_scroll >= 0:
      self.queued_scroll = rem_scroll
      self.spam_once()

  def on_scroll(self, x, y, dx, dy):
    # queue scroll actions
    self.queued_scroll += abs(dx) + abs(dy)

  def spam_once(self):
    # check whether the selected region exceeds the threshold
    img = masked_screenshot(self.select_region, self.cross_kernel)
    area,_ = measure_bright_box(img)
    if area > self.select_threshold:
      self.exit_spam_mode()
    else:
      self.mouse_sim.click(mouse.Button.left)

def main():
  root = Tk()
  Application(root)
  root.mainloop()

if __name__ == '__main__':
  main()
