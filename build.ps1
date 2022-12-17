#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
# single file for portable distribution
pyinstaller --onefile --windowed --icon='./img/logo.ico' --name='PoE High Spammer' --splash='./img/banner.png' --add-data='./img/logo.ico;img' --add-data='./img/banner.png;img/' launch.pym
# multi file for innosetup distribution
pyinstaller --onedir --windowed --icon='./img/logo.ico' --name='PoE High Spammer' --splash='./img/banner.png' --add-data='./img/logo.ico;img' --add-data='./img/banner.png;img/' --strip launch.py
iscc /Q .\setup.iss
