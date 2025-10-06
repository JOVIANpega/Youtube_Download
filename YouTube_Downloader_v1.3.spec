# -*- mode: python ; coding: utf-8 -*-

import os, sys
# Ensure project root is on sys.path for imports during spec execution
sys.path.insert(0, os.path.abspath('.'))

from version_info import VERSION

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('config', 'config'), ('assets', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=f'YouTube_Downloader_v{VERSION}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
