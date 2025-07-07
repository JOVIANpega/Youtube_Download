#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
多平台影片下載器 - 構建可執行文件腳本
版本: 1.71
"""

import os
import sys
import shutil
import subprocess
import platform
import time
import re

# 檢查 Python 版本
if sys.version_info < (3, 6):
    print("錯誤: 需要 Python 3.6 或更高版本")
    sys.exit(1)

# 檢查必要的模組
try:
    import PyInstaller
except ImportError:
    print("正在安裝 PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

# 獲取當前目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
build_dir = os.path.join(current_dir, "build")
dist_dir = os.path.join(current_dir, "dist")
temp_dir = os.path.join(current_dir, "build_temp")

# 確保目錄存在
os.makedirs(temp_dir, exist_ok=True)

# 版本信息
version = "1.71"
app_name = "多平台影片下載器"
exe_name = f"{app_name}_v{version}"

# 更新版本信息文件
with open(os.path.join(temp_dir, "version_info.txt"), "w", encoding="utf-8") as f:
    f.write(f"版本: {version}\n")
    f.write(f"構建時間: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"系統: {platform.system()} {platform.version()}\n")
    f.write(f"Python: {platform.python_version()}\n")

print(f"=== 開始構建 {app_name} v{version} ===")

# 清理之前的構建
if os.path.exists(build_dir):
    print("清理構建目錄...")
    shutil.rmtree(build_dir, ignore_errors=True)
if os.path.exists(dist_dir):
    print("清理發布目錄...")
    shutil.rmtree(dist_dir, ignore_errors=True)

# 安裝/更新依賴
print("檢查並安裝依賴...")
with open(os.path.join(current_dir, "requirements.txt"), "r") as f:
    requirements = f.read().splitlines()

for req in requirements:
    if req and not req.startswith("#"):
        print(f"安裝 {req}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-U", req])
        except subprocess.CalledProcessError:
            print(f"警告: 安裝 {req} 失敗，嘗試繼續...")

# 創建啟動腳本
print("創建啟動腳本...")
start_script = os.path.join(current_dir, f"start_v{version}.py")
with open(start_script, "w", encoding="utf-8") as f:
    f.write(f"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-

\"\"\"
多平台影片下載器 - 啟動腳本
版本: {version}
\"\"\"

import os
import sys
import subprocess
import importlib.util
import time

# 添加當前目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加src目錄到路徑
src_dir = os.path.join(current_dir, "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 檢查並安裝必要的套件
required_packages = ["yt-dlp", "PySide6"]

def install_package(package):
    \"\"\"安裝套件\"\"\"
    print(f"正在安裝 {{package}}...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except Exception as e:
        print(f"安裝 {{package}} 失敗: {{str(e)}}")
        return False

# 安裝必要的套件
for package in required_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        if not install_package(package):
            print(f"無法安裝 {{package}}，程式可能無法正常運行")
            time.sleep(3)

# 啟動主程式
try:
    from src.tabbed_gui_demo import main
    main()
except ImportError as e:
    print(f"導入主程式失敗: {{str(e)}}")
    print("嘗試直接執行主程式...")
    try:
        # 直接執行主程式檔案
        script_path = os.path.join(src_dir, "tabbed_gui_demo.py")
        if os.path.exists(script_path):
            subprocess.call([sys.executable, script_path])
        else:
            print(f"找不到主程式檔案: {{script_path}}")
    except Exception as e:
        print(f"執行主程式時發生錯誤: {{str(e)}}")
    
    # 等待用戶輸入，避免視窗立即關閉
    input("按Enter鍵退出...") 
""")

# 創建簡化的啟動腳本
simple_start_script = os.path.join(current_dir, f"start_downloader_v{version}.py")
shutil.copy(start_script, simple_start_script)

# 構建可執行文件
print("構建可執行文件...")
icon_path = os.path.join(current_dir, "assets", "icon.ico")
if not os.path.exists(icon_path):
    icon_path = os.path.join(current_dir, "assets", "icon.png")

# 確定 ffmpeg 目錄
ffmpeg_dir = os.path.join(current_dir, "ffmpeg_bin")

# 構建命令
cmd = [
    "pyinstaller",
    "--noconfirm",
    "--clean",
    "--name", exe_name,
    "--add-data", f"{src_dir};src",
    "--add-data", f"{temp_dir};build_temp",
]

# 添加 ffmpeg 目錄（如果存在）
if os.path.exists(ffmpeg_dir):
    cmd.extend(["--add-data", f"{ffmpeg_dir};ffmpeg_bin"])

# 添加圖標（如果存在）
if os.path.exists(icon_path):
    cmd.extend(["--icon", icon_path])

# 添加其他選項
cmd.extend([
    "--onefile",
    "--windowed",
    start_script
])

# 執行構建
print("執行 PyInstaller...")
print(" ".join(cmd))
subprocess.call(cmd)

# 複製必要的文件到發布目錄
print("複製必要文件到發布目錄...")
if os.path.exists(dist_dir):
    # 複製 README 和 LICENSE
    for file in ["README.md", "LICENSE", "RELEASE_NOTES_V1.71.md"]:
        if os.path.exists(os.path.join(current_dir, file)):
            shutil.copy(os.path.join(current_dir, file), os.path.join(dist_dir, file))
    
    # 創建空的 cookies.txt 文件
    with open(os.path.join(dist_dir, "cookies.txt"), "w") as f:
        f.write("# 在此處放置您的 cookies\n")
    
    # 創建使用說明
    with open(os.path.join(dist_dir, "使用說明.md"), "w", encoding="utf-8") as f:
        f.write(f"""# {app_name} v{version} 使用說明

## 基本使用
1. 運行 `{exe_name}.exe` 啟動程式
2. 在輸入框中貼上影片連結（支援多個連結，每行一個）
3. 選擇下載格式和解析度
4. 點擊「開始下載」按鈕

## 支援的平台
- YouTube
- TikTok / 抖音
- Facebook
- Instagram
- Bilibili
- X (Twitter)
- 更多平台持續增加中...

## 特殊功能
- 批量下載：每行輸入一個連結，可同時下載多個影片
- 格式選擇：支援下載最高品質、僅視頻、僅音訊等多種格式
- 解析度選擇：可選擇不同解析度
- 自動合併：自動合併視頻和音訊
- 檔名前綴：可添加自定義前綴
- 視窗大小記憶：程式會記住您上次調整的視窗大小和位置

## 常見問題
- 如果下載失敗，請嘗試使用不同的格式或解析度
- 某些需要登入的內容可能需要提供 cookies.txt 檔案
- 如遇到問題，請查看錯誤訊息或嘗試使用錯誤對話框中提供的外部下載工具

## 更新日誌
請查看 `RELEASE_NOTES_V{version}.md` 檔案了解最新更新內容。
""")

    print(f"發布目錄準備完成: {dist_dir}")

print(f"=== {app_name} v{version} 構建完成 ===") 