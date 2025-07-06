#!/usr/bin/env python3
"""
YouTube下載器 V1.63 簡化打包腳本
"""

import os
import sys
import subprocess
from pathlib import Path

print("=" * 50)
print("YouTube下載器 V1.63 簡化打包腳本")
print("=" * 50)

# 檢查PyInstaller
try:
    import PyInstaller
    print("✓ 已安裝 PyInstaller")
except ImportError:
    print("✗ 未安裝 PyInstaller，正在安裝...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    print("✓ PyInstaller 安裝完成")

# 獲取當前目錄
script_dir = Path(__file__).parent.absolute()
src_dir = script_dir / "src"

# 創建啟動腳本
start_script = script_dir / "start_downloader_v1.63.py"
if not os.path.exists(start_script):
    print(f"啟動腳本不存在，已經在之前創建")

# 運行PyInstaller
print("\n開始打包...")
cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--onefile",
    "--name", "youtube_downloader_v1.63",
    "--add-data", f"{src_dir};src",
    str(start_script)
]

print(f"執行命令: {' '.join(cmd)}")
subprocess.run(cmd)

print("\n打包完成!")
print("=" * 50) 