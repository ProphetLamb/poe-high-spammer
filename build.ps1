#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-
# single file for portable distribution
pyinstaller --onefile --windowed --icon='./assets/logo.ico' --name='PoE High Spammer' --splash='./assets/banner.png' --add-data='./assets/*;assets/' --strip ./src/launch.py
# multi file for innosetup distribution
pyinstaller --onedir --windowed --icon='./assets/logo.ico' --name='PoE High Spammer' --splash='./assets/banner.png' --add-data='./assets/*;assets/' --strip ./src/launch.py
iscc /Q .\setup.iss
