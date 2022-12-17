#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tkinter import *
import pyautogui
import scipy.ndimage
import scipy
import numpy as np
from pynput import keyboard, mouse
import random

def masked_screenshot(region: tuple) -> np.ndarray:
  """Take a screenshot of the given region and apply some processing to it.
  Args:
      region (tuple): the region from top-left in the form (x1, y1, x2, y2)
  Returns:
      np.ndarray: the monochrome screenshot taken from the given region
  """
  img = pyautogui.screenshot(region=region)
  # convert the image to a grayscale numpy array
  img = np.array(img.convert('L'))
  # apply thresholding
  # the dark box will turn bright if its a match, so we ought to remove the dark, but keep the bright over the thresholdm
  # the theshold is 100, so anything below 100 will be set to 0, anything above 100 will be set to 255
  # now the dark box will be 0, and the bright box will be 255, which can easily be detected using the scipy.ndimage.morphology
  img = (img > 100) * 255
  # finally apply dilation and erosion to remove some noise
  kernel = np.ones((2, 2), np.uint8)
  img = scipy.ndimage.morphology.binary_dilation(img, structure=kernel).astype(img.dtype)
  img = scipy.ndimage.morphology.binary_erosion(img, structure=kernel).astype(img.dtype)
  return img

def measure_bright_box(mask: np.ndarray) -> int:
  labels, n = scipy.ndimage.measurements.label(mask, np.ones((3, 3)))
  # get the bounding boxes of the bright boxes
  bboxes = scipy.ndimage.measurements.find_objects(labels)
  # get the largest bounding box
  largest_bbox = max(bboxes, key=lambda bbox: (bbox[0].stop - bbox[0].start) * (bbox[1].stop - bbox[1].start))
  # return the area of the largest bounding box
  return (largest_bbox[0].stop - largest_bbox[0].start) * (largest_bbox[1].stop - largest_bbox[1].start)

class Application():
  def __init__(self, master):
    self.snip_surface = None
    self.master = master
    self.start_x = None
    self.start_y = None
    self.current_x = None
    self.current_y = None
    self.select_region = None
    self.select_threshold = None
    self.hotkey_keycode = None
    self.hotkey_listener = None
    self.spammer_active = False

    root.geometry('400x400+200+200')  # set new geometry
    root.title('POE High Spammer')

    # menu frame
    self.menu_frame = Frame(master)
    self.menu_frame.pack(fill=BOTH, expand=YES, padx=1, pady=1)

    # selection
    Label(self.menu_frame, text="selection").pack(side="top", fill="x")
    # selection ui
    select = Frame(self.menu_frame, height=5, bg="")
    select.pack(side="top", fill="x")
    Label(select, text="select area").pack(side="left", fill="y")
    self.select_btn = Button(select, command=self.enter_select_mode, text="region")
    self.select_btn.pack(side="right", fill="y")
    self.select_lbl = Label(select, text="")
    self.select_lbl.pack(side="right", fill="y")
    # selection threshold
    threshold = Frame(self.menu_frame, height=5, bg="")
    threshold.pack(side="top", fill="x")
    Label(threshold, text="area threshold").pack(side="left", fill="y")
    # numeric threshold input which sets self.select_threshold
    self.threshold_entry = Entry(threshold, width=5)
    self.threshold_entry.pack(side="right", fill="y")
    self.threshold_entry.insert(0, "4000")
    self.threshold_entry.bind("<Tab>", self.on_threshold_change)

    # auto-clicker
    Label(self.menu_frame, text="auto-clicker").pack(side="top", fill="x")
    # hotkey
    hotkey = Frame(self.menu_frame, height=5, bg="")
    hotkey.pack(side="top", fill="x")
    Label(hotkey, text="hotkey").pack(side="left", fill="y")
    self.hotkey_edit_btn = Button(hotkey, command=self.enter_hotkey_mode, text="edit")
    self.hotkey_edit_btn.pack(side="right", fill="y")
    self.hotkey_edit_label = Label(hotkey, text="None")
    self.hotkey_edit_label.pack(side="right", fill="y")
    # spammer
    spammer = Frame(self.menu_frame, height=5, bg="")
    spammer.pack(side="top", fill="x")
    Label(spammer, text="spammer").pack(side="left", fill="y")
    self.spammer_lbl = Label(spammer, text="inactive", fg="red")
    self.spammer_lbl.pack(side="right", fill="y")

    # selector overlay
    self.master_screen = Toplevel(root)
    self.master_screen.withdraw()
    self.master_screen.attributes("-transparent", "maroon3")
    self.picture_frame = Frame(self.master_screen, background="maroon3")
    self.picture_frame.pack(fill=BOTH, expand=YES)

  def enter_select_mode(self):
    self.master_screen.deiconify()
    root.withdraw()

    self.snip_surface = Canvas(self.picture_frame, cursor="cross", bg="grey11")
    self.snip_surface.pack(fill=BOTH, expand=YES)

    self.snip_surface.bind("<ButtonPress-1>", self.on_select_button_press)
    self.snip_surface.bind("<B1-Motion>", self.on_select_drag)
    self.snip_surface.bind("<ButtonRelease-1>", self.on_select_button_release)

    self.master_screen.attributes('-fullscreen', True)
    self.master_screen.attributes('-alpha', .3)
    self.master_screen.lift()
    self.master_screen.attributes("-topmost", True)

  def set_select(self, x1, y1, x2, y2):
    self.select_region = (x1, y1, x2, y2)
    img = masked_screenshot(self.select_region)
    area = measure_bright_box(img)

    self.select_lbl["text"] = "largest rect {}px".format(area)

    # update the threshold based on the area
    # use 90% of the area rounded down to a multiple of 100 to avoid false positives
    thres = int((area * .9) / 100) * 100
    self.threshold_entry.insert(0, str(thres))
    self.on_threshold_change(None)

  def on_select_button_release(self, event):
    if self.start_x <= self.current_x and self.start_y <= self.current_y:
      self.set_select(self.start_x, self.start_y, self.current_x - self.start_x, self.current_y - self.start_y)

    elif self.start_x >= self.current_x and self.start_y <= self.current_y:
      self.set_select(self.current_x, self.start_y, self.start_x - self.current_x, self.current_y - self.start_y)

    elif self.start_x <= self.current_x and self.start_y >= self.current_y:
      self.set_select(self.start_x, self.current_y, self.current_x - self.start_x, self.start_y - self.current_y)

    elif self.start_x >= self.current_x and self.start_y >= self.current_y:
      self.set_select(self.current_x, self.current_y, self.start_x - self.current_x, self.start_y - self.current_y)

    self.exit_select_mode()
    return event

  def exit_select_mode(self):
    self.snip_surface.destroy()
    self.master_screen.withdraw()
    root.deiconify()

  def on_select_button_press(self, event):
    # save mouse drag start position
    self.start_x = self.snip_surface.canvasx(event.x)
    self.start_y = self.snip_surface.canvasy(event.y)
    self.snip_surface.create_rectangle(0, 0, 1, 1, outline='red', width=3, fill="maroon3")

  def on_select_drag(self, event):
    self.current_x, self.current_y = (event.x, event.y)
    # expand rectangle as you drag the mouse
    self.snip_surface.coords(1, self.start_x, self.start_y, self.current_x, self.current_y)

  def on_threshold_change(self, event):
    self.select_threshold = int(self.threshold_entry.get())
    print(self.select_threshold)

  def enter_hotkey_mode(self):
    self.hotkey_edit_btn["text"] = "stop"
    self.hotkey_edit_btn["command"] = self.exit_hotkey_mode
    self.hotkey_edit_btn.pack(side="right", fill="y")
    self.master.bind("<Key>", self.on_hotkey_press)
    # stop listening to the hotkey
    if self.hotkey_listener is not None:
      self.hotkey_listener.stop()
      self.hotkey_listener = None

  def exit_hotkey_mode(self):
    self.hotkey_edit_btn["text"] = "edit"
    self.hotkey_edit_btn["command"] = self.enter_hotkey_mode
    self.hotkey_edit_btn.pack(side="right", fill="y")
    self.master.unbind("<Key>")
    # start listening to the hotkey
    self.hotkey_listener = keyboard.Listener(on_press=self.on_spammer_triggered)
    self.hotkey_listener.start()

  def on_hotkey_press(self, event):
    # unbind previous from master
    self.hotkey_keycode = event.keycode
    self.hotkey_edit_label["text"] = event.keysym


  def on_spammer_triggered(self, event):
    if not hasattr(event, "vk"):
      return self.on_spammer_triggered(event.value)
    if self.hotkey_keycode == event.vk:
      if self.spammer_active:
        self.exit_spam_mode()
      else:
        self.enter_spam_mode()

  def enter_spam_mode(self):
    self.spammer_lbl["text"] = "active"
    self.spammer_lbl["fg"] = "green"
    # active the spammer
    self.spammer_active = True
    self.spam()


  def exit_spam_mode(self):
    self.spammer_lbl["text"] = "inactive"
    self.spammer_lbl["fg"] = "red"
    # deactivate the spammer
    self.spammer_active = False

  def spam(self):
    if not self.spammer_active:
      return
    root.after(200 + random.randrange(0, 100), self.spam)

    # check whether the selected region exceeds the threshold
    img = masked_screenshot(self.select_region)
    area = measure_bright_box(img)
    if area > self.select_threshold:
      self.exit_spam_mode()
    else:
      mouse_sim.click(mouse.Button.left)

if __name__ == '__main__':
  mouse_sim = mouse.Controller()
  root = Tk()
  root.resizable(width=False, height=False)
  app = Application(root)
  root.mainloop()
