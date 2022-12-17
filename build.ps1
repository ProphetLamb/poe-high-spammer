#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
pyinstaller --onefile --windowed --icon='./img/logo.ico' --name='PoE High Spammer' --splash='./img/banner.png' --add-data='./img/logo.ico;img' --add-data='./img/banner.png;img/' launch.py
