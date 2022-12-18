#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (c) 2022, ProphetLamb <prophet.lamb@gmail.com>
#
# This file acts as the main entry point for the application, when launching from a binary compiled by PyInstaller.
# It is not used when launching from source, instead main.py is used as the entry point.
# In order to access assets in PyInstaller, we need to change the working directory to the directory containing the assets.

import sys
import os
import main
import pyi_splash

os.chdir(sys._MEIPASS)
pyi_splash.close()
main.main()
