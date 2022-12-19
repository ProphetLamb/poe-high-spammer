#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# Build
# -----------------------------------------------------------------------------
# pyinstaller common options
$pyinstaller_options = @(
  '--windowed'
  '--icon=./assets/logo.ico'
  '--name=PoE High Spammer'
  '--splash=./assets/banner.png'
  '--add-data=./assets/*;assets'
  '--strip'
  './src/launch.py'
)
# single file for portable distribution
pyinstaller --onefile $pyinstaller_options
# multi file for innosetup distribution
pyinstaller --onedir $pyinstaller_options
iscc /Q .\setup.iss

# -----------------------------------------------------------------------------
# Cleanup
# -----------------------------------------------------------------------------
# outputs to ./dist/[PoE High Spammer.exe, PoE High Spammer - Setup.exe, PoE High Spammer/] and ./PoE High Spammer Setup.spec
# rename to dist/[poe-high-spammer-portable.exe, poe-high-spamme-setup.exe], remove dist/PoE High Spammer/ and PoE High Spammer Setup.spec
Move-Item -Force '.\dist\PoE High Spammer.exe' '.\dist\poe-high-spammer-portable.exe'
Move-Item -Force '.\dist\PoE High Spammer - Setup.exe' '.\dist\poe-high-spammer-setup.exe'
Remove-Item -Recurse '.\dist\PoE High Spammer\'
Remove-Item '.\PoE High Spammer.spec'
