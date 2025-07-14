import os
import sys
import shutil
import subprocess
from datetime import datetime

# 版本信息
VERSION = "1.72"
VERSION_INFO = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 7, 2, 0),
    prodvers=(1, 7, 2, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Multi-Platform Video Downloader'),
         StringStruct(u'FileDescription', u'多平台影片下載器 V{VERSION} - 支援YouTube、TikTok、Facebook、Instagram、Bilibili、X/Twitter，記憶使用者設定與視窗狀態'),
         StringStruct(u'FileVersion', u'1.7.2'),
         StringStruct(u'InternalName', u'multi_platform_downloader'),
         StringStruct(u'LegalCopyright', u'Copyright (c) 2024-2025'),
         StringStruct(u'OriginalFilename', u'多平台影片下載器.exe'),
         StringStruct(u'ProductName', u'多平台影片下載器'),
         StringStruct(u'ProductVersion', u'1.7.2')])
    ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

def create_version_file():
    """創建版本信息文件"""
    with open("version_file.txt", "w", encoding="utf-8") as f:
        f.write(VERSION_INFO)
    return "version_file.txt"

def create_start_script():
    """創建啟動腳本"""
    script_name = f"start_v{VERSION}.py"
    with open(script_name, "w", encoding="utf-8") as f:
        f.write(f"""import os
import sys
from src.tabbed_gui_demo import main

if __name__ == "__main__":
    # 設置版本號
    os.environ["APP_VERSION"] = "{VERSION}"
    
    # 檢查是否是打包後的環境
    if getattr(sys, 'frozen', False):
        # 設置資源路徑
        os.environ["RESOURCE_PATH"] = os.path.join(sys._MEIPASS, "assets")
    else:
        # 開發環境
        os.environ["RESOURCE_PATH"] = "assets"
    
    # 啟動主程序
    main()
""")
    return script_name

def create_downloader_script():
    """創建下載器啟動腳本"""
    script_name = f"start_downloader_v{VERSION}.py"
    with open(script_name, "w", encoding="utf-8") as f:
        f.write(f"""import os
import sys
from src.tabbed_gui_demo import main

if __name__ == "__main__":
    # 設置版本號
    os.environ["APP_VERSION"] = "{VERSION}"
    
    # 檢查是否是打包後的環境
    if getattr(sys, 'frozen', False):
        # 設置資源路徑
        os.environ["RESOURCE_PATH"] = os.path.join(sys._MEIPASS, "assets")
        os.environ["FFMPEG_PATH"] = os.path.join(sys._MEIPASS, "ffmpeg_bin")
    else:
        # 開發環境
        os.environ["RESOURCE_PATH"] = "assets"
        os.environ["FFMPEG_PATH"] = "ffmpeg_bin"
    
    # 啟動主程序
    main()
""")
    return script_name

def update_version_file():
    """更新VERSION文件"""
    with open("VERSION", "w") as f:
        f.write(f"{VERSION}\n")

def build_exe():
    """構建可執行文件"""
    # 創建必要的文件
    version_file = create_version_file()
    start_script = create_downloader_script()
    update_version_file()
    
    # 確保目標目錄存在
    os.makedirs("dist", exist_ok=True)
    
    # 構建命令
    cmd = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--icon=assets/icon.ico",
        f"--name=多平台影片下載器_V{VERSION}",
        f"--version-file={version_file}",
        "--add-data=assets;assets",
        "--add-data=ffmpeg_bin;ffmpeg_bin",
        start_script
    ]
    
    # 執行構建
    print(f"開始構建 V{VERSION} 版本...")
    subprocess.run(cmd, check=True)
    
    # 清理臨時文件
    print("清理臨時文件...")
    if os.path.exists(version_file):
        os.remove(version_file)
    
    print(f"構建完成! 輸出文件: dist/多平台影片下載器_V{VERSION}.exe")

if __name__ == "__main__":
    # 記錄開始時間
    start_time = datetime.now()
    print(f"開始時間: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        build_exe()
        
        # 計算耗時
        end_time = datetime.now()
        duration = end_time - start_time
        print(f"結束時間: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"總耗時: {duration}")
        
        print("\n構建成功!")
    except Exception as e:
        print(f"構建失敗: {e}")
        sys.exit(1) 