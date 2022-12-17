#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
from tkinter import *
from pynput import keyboard, mouse
import random
from PIL import Image, ImageTk
from oir import masked_screenshot, measure_bright_box, get_cross_kernel

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
    self.legal_mode = True
    self.scroll_listener = None
    self.queued_scroll = 0
    self.mouse_sim = mouse.Controller()
    self.cross_kernel = get_cross_kernel(5)

    banner = Image.open("./img/banner.png")
    banner = banner.resize((WIDTH, int(WIDTH * banner.height / banner.width)), Image.ANTIALIAS)
    banner_wd = ImageTk.PhotoImage(banner)
    lbl=Label(root, image=banner_wd)
    lbl.image = banner_wd
    lbl.pack()

    # menu frame
    self.menu_frame = Frame(master, bg="white")
    self.menu_frame.pack(side="top", fill="x", expand='yes')

    # selection
    Label(self.menu_frame, text="selection").pack(side="top", fill="x")
    # selection ui
    select = Frame(self.menu_frame, height=5, bg="", padx=5, pady=5)
    select.pack(side="top", fill="x")
    Label(select, text="select area", bg="white").pack(side="left", fill="y")
    self.select_btn = Button(select, command=self.enter_select_mode, text="region")
    self.select_btn.pack(side="right", fill="y")
    self.select_lbl = Label(select, text="none", bg="white")
    self.select_lbl.pack(side="right", fill="y")
    # selection threshold
    threshold = Frame(self.menu_frame, height=5, bg="", padx=5, pady=5)
    threshold.pack(side="top", fill="x")
    Label(threshold, text="area threshold", bg="white").pack(side="left", fill="y")
    # numeric threshold input which sets self.select_threshold
    self.threshold_entry = Entry(threshold, width=5)
    self.threshold_entry.pack(side="right", fill="y")
    self.threshold_entry.insert(0, "4000")
    self.threshold_entry.bind("<Tab>", self.on_threshold_change)

    # auto-clicker
    Label(self.menu_frame, text="spammer").pack(side="top", fill="x")
    # hotkey
    hotkey = Frame(self.menu_frame, height=5, bg="", padx=5, pady=5)
    hotkey.pack(side="top", fill="x")
    Label(hotkey, text="hotkey", bg="white").pack(side="left", fill="y")
    self.hotkey_edit_btn = Button(hotkey, command=self.enter_hotkey_mode, text="edit")
    self.hotkey_edit_btn.pack(side="right", fill="y")
    self.hotkey_edit_label = Label(hotkey, text="none", bg="white")
    self.hotkey_edit_label.pack(side="right", fill="y")
    # spammer
    spammer = Frame(self.menu_frame, height=5, bg="", padx=5, pady=5)
    spammer.pack(side="top", fill="x")
    Label(spammer, text="spammer", bg="white").pack(side="left", fill="y")
    self.spammer_lbl = Label(spammer, text="inactive", fg="red", bg="white")
    self.spammer_lbl.pack(side="right", fill="y")
    # legal mode
    # legal = Frame(self.menu_frame, height=5, bg="")
    # legal.pack(side="top", fill="x")
    # Label(legal, text="legal mode").pack(side="left", fill="y")
    # self.legal_btn = Button(legal, command=self.toggle_legal_mode, text="on")
    # self.legal_btn.pack(side="right", fill="y")

    # selector overlay
    self.master_screen = Toplevel(root)
    self.master_screen.withdraw()
    self.master_screen.attributes("-transparent", "maroon3")
    self.picture_frame = Frame(self.master_screen, background="maroon3")
    self.picture_frame.pack(fill=BOTH, expand=YES)

  # -----------------------------------------------------------------------------
  # REGION SELECTION
  # -----------------------------------------------------------------------------

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
    self.master_screen.bind("<Escape>", self.on_select_cancel)

  def exit_select_mode(self):
    self.snip_surface.destroy()
    self.master_screen.unbind("<Escape>")
    self.master_screen.withdraw()
    root.deiconify()

  def on_select_cancel(self, event):
    self.exit_select_mode()
    return event

  def set_select(self, x1, y1, x2, y2):
    self.select_region = (x1, y1, x2, y2)
    img = masked_screenshot(self.select_region, self.cross_kernel)
    box_area = measure_bright_box(img)
    img_area = img.shape[0] * img.shape[1]
    fill_ratio = box_area / float(img_area) * 100

    self.select_lbl["text"] = "found {}px² in {}px² ({:2.2f}%)".format(box_area, img_area, fill_ratio)

    # update the threshold based on the area
    # use 90% of the area rounded down to a multiple of 100 to avoid false positives
    thres = int((box_area * .95) / 100) * 100
    self.threshold_entry.delete(0, END)
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

  def on_select_button_press(self, event):
    # save mouse drag start position
    self.start_x = self.snip_surface.canvasx(event.x)
    self.start_y = self.snip_surface.canvasy(event.y)
    self.snip_surface.create_rectangle(0, 0, 1, 1, outline='red', width=3, fill="maroon3")
    return event

  def on_select_drag(self, event):
    self.current_x, self.current_y = (event.x, event.y)
    # expand rectangle as you drag the mouse
    self.snip_surface.coords(1, self.start_x, self.start_y, self.current_x, self.current_y)
    return event

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
    return event

  def toggle_legal_mode(self):
    self.legal_mode = not self.legal_mode
    self.legal_btn["text"] = "on" if self.legal_mode else "off"

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
    if self.legal_mode:
      self.begin_spam_legal()
    else:
      self.begin_spam_illegal()

  def exit_spam_mode(self):
    self.spammer_lbl["text"] = "inactive"
    self.spammer_lbl["fg"] = "red"
    # deactivate the spammer
    self.spammer_active = False
    if self.legal_mode:
      self.stop_spam_legal()
    else:
      self.stop_spam_illegal()

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
    root.after(140 + random.randrange(0, 110), self.spam_legal_loop)
    rem_scroll = self.queued_scroll - 1
    if rem_scroll >= 0:
      self.queued_scroll = rem_scroll
      self.spam_once()

  def on_scroll(self, x, y, dx, dy):
    # queue scroll actions
    self.queued_scroll += abs(dx) + abs(dy)

  # -----------------------------------------------------------------------------
  # ILLEGAL SPAMMING
  # -----------------------------------------------------------------------------

  def begin_spam_illegal(self):
    self.spam_illegal_loop()

  def stop_spam_illegal(self):
    pass

  def spam_illegal_loop(self):
    """ repeats left mouse clicks in random intervals around 4Hz
    """
    if not self.spammer_active:
      return
    root.after(190 + random.randrange(0, 110), self.spam_illegal_loop)
    self.spam_once()

  def spam_once(self):
    # check whether the selected region exceeds the threshold
    img = masked_screenshot(self.select_region, self.cross_kernel)
    area = measure_bright_box(img)
    if area > self.select_threshold:
      self.exit_spam_mode()
    else:
      self.mouse_sim.click(mouse.Button.left)

def main():
  global root,app,WIDTH,HEIGHT
  root = Tk()

  WIDTH, HEIGHT = 400, 600
  root.resizable(width=False, height=False)
  root.geometry('{}x{}+200+200'.format(WIDTH, HEIGHT))
  root.title('PoE High Spammer')
  root.iconbitmap("./img/logo.ico")

  app = Application(root)

  Label(root, text="Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>").pack(side="bottom", fill="x")
  root.mainloop()

if __name__ == '__main__':
  main()
