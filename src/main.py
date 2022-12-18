#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
#
# This is the main entry point for the application, when launching from source.
# It contains the main Tkinter application loop, and is responsible for creating the main window and all of its components.

from oir import get_cross_kernel, largest_bbox, masked_screenshot, measure_bright_box, render_bboxes, smart_resize
from PIL import Image as PilImage, ImageTk
from snipper import Snipper
from spammer import Spammer
from tkinter import *
from hotkey import HK_BIND, HK_LISTEN, Hotkey, canonicalize
import numpy as np
import typing as t

class Application():
  def __init__(self, master: Tk):
    # -----------------------------------------------------------------------------
    # Properties
    # -----------------------------------------------------------------------------
    self.master = master
    self.select_threshold = None
    self.select_region = None
    self.cross_kernel = get_cross_kernel(5, 3)

    # hotkey
    self.hotkey = Hotkey()
    self.hotkey.set_bind_cb(self.on_hotkey_bind)
    self.hotkey.set_activate_cb(self.on_hotkey_activate)

    # spammer
    self.spammer = Spammer(master)
    self.spammer.set_spam_cb(self.on_spam)

    # snipper
    self.snipper = Snipper(master)
    self.snipper.set_select_cb(self.on_select)

    # -----------------------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------------------
    width, height = 400, 650

    master.resizable(width=False, height=False)
    master.geometry('{}x{}+200+200'.format(width, height))
    master.title('PoE High Spammer')
    master.iconbitmap("./assets/logo.ico")

    banner = PilImage.open("./assets/banner.png")
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

    # counter
    self.spammer_counter_lbl = Label(self.menu_frame, text="0 attempts, 0 remaining", bg="white", fg="#FA2FBD")
    self.spammer_counter_lbl.pack(side=TOP, fill=X)

    # copyright
    Label(master, text="Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>").pack(side="bottom", fill=X)

  # -----------------------------------------------------------------------------
  # Update UI
  # -----------------------------------------------------------------------------

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

  def update_preview_lbl(self, img: np.ndarray, bboxes: t.List[tuple], success: bool = False, failed: bool = False):
    background_color = (60,250,146) if success else (251,148,220) if failed else None
    img = render_bboxes(img, bboxes, background_color=background_color)
    img = PilImage.fromarray(img)
    # fix height to 250px
    img = smart_resize(img, height=250)
    img_wg = ImageTk.PhotoImage(img)
    self.preview_lbl.configure(image=img_wg)
    self.preview_lbl.image = img_wg

  def update_counter_lbl(self):
    self.spammer_counter_lbl["text"] = "{} attempts, {} remaining".format(self.spammer.get_count(), self.spammer.get_queued_count())

  # -----------------------------------------------------------------------------
  # REGION SELECTION
  # -----------------------------------------------------------------------------

  def enter_select_mode(self):
    self.snipper.enter_select_mode()

  def on_select(self, region: t.Tuple[int, int, int, int]):
    self.select_region = region
    img = masked_screenshot(region, self.cross_kernel)
    bboxes = measure_bright_box(img)
    box_area = largest_bbox(bboxes)

    self.update_select_lbl(img, box_area)
    self.update_preview_lbl(img, bboxes)
    self.update_threshold(box_area)

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
    self.hotkey.set_mode(HK_BIND)

  def exit_hotkey_mode(self):
    self.hotkey_edit_btn["text"] = "edit"
    self.hotkey_edit_btn["command"] = self.enter_hotkey_mode
    self.hotkey_edit_btn.pack(side=RIGHT, fill=Y)
    self.hotkey.set_mode(HK_LISTEN)

  def on_hotkey_bind(self, key):
    self.hotkey_edit_label["text"] = canonicalize(key)
    self.hotkey_edit_label["fg"] = "black"
    return key

  # -----------------------------------------------------------------------------
  # SPAMMER TOGGLE
  # -----------------------------------------------------------------------------

  def on_hotkey_activate(self, key):
    if self.spammer.is_active():
      self.exit_spam_mode()
    else:
      self.enter_spam_mode()
    return key

  def enter_spam_mode(self):
    self.spammer_lbl["text"] = "active"
    self.spammer_lbl["fg"] = "green"
    self.spammer.start()
    # update the window
    # this fixes a bug where the window would be psudo-frozen and not update before tickled by user interaction.
    # this means, that the code would execute, and even the event=loop processed, but the visual update would not happen
    # updating the window manually doesn't fix this, but focusing in addition to the update does
    def upd():
      self.master.update()
      self.master.focus_force()
    self.master.after(50, upd)

  def exit_spam_mode(self):
    self.spammer_lbl["text"] = "inactive"
    self.spammer_lbl["fg"] = "red"
    self.spammer.stop()

  def on_spam(self) -> bool:
    mask = masked_screenshot(self.select_region, self.cross_kernel)
    bboxes = measure_bright_box(mask)
    if self.select_threshold is None:
      self.after_spam(mask, bboxes, failed=True)
      return False
    area = largest_bbox(bboxes)
    if area >= self.select_threshold:
      self.after_spam(mask, bboxes, success=True)
      return False
    self.after_spam(mask, bboxes)
    return True

  def after_spam(self, mask, bboxes, success = False, failed = False):
    self.update_preview_lbl(mask, bboxes, success, failed)
    self.update_counter_lbl()
    if success or failed:
      self.exit_spam_mode()
    self.master.after_idle(self.master.update)

def main():
  root = Tk()
  Application(root)
  root.mainloop()

if __name__ == '__main__':
  main()
