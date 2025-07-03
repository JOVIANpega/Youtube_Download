#!/usr/bin/env python3
"""
YouTube下載器 V1.63 極簡打包腳本
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

print("=" * 50)
print("YouTube下載器 V1.63 極簡打包腳本")
print("=" * 50)

# 獲取當前目錄
script_dir = Path(__file__).parent.absolute()
src_dir = script_dir / "src"
dist_dir = script_dir / "dist"
build_dir = script_dir / "build"

# 清理舊的構建目錄
if dist_dir.exists():
    shutil.rmtree(dist_dir)
if build_dir.exists():
    shutil.rmtree(build_dir)

# 創建啟動腳本
start_script = """
import sys
import os
from pathlib import Path

# 添加src目錄到路徑
script_dir = Path(__file__).parent.absolute()
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# 導入主模組
try:
    from tabbed_gui_demo import main
    main()
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
    input("按Enter鍵退出...")
"""

# 創建臨時啟動文件
temp_start_file = script_dir / "temp_start.py"
with open(temp_start_file, "w", encoding="utf-8") as f:
    f.write(start_script)

print("開始打包...")

# 使用PyInstaller打包
cmd = [
    sys.executable,
    "-m", "PyInstaller",
    "--name=youtube_downloader_v1.63",
    "--onefile",
    "--windowed",
    str(temp_start_file)
]

try:
    subprocess.run(cmd, check=True)
    print("打包完成!")
    
    # 清理臨時文件
    if temp_start_file.exists():
        os.remove(temp_start_file)
    
    # 檢查結果
    exe_file = dist_dir / "youtube_downloader_v1.63.exe"
    if exe_file.exists():
        print(f"成功創建: {exe_file}")
    else:
        print("打包失敗: 未找到輸出文件")
        
except Exception as e:
    print(f"打包過程中出錯: {e}")

print("=" * 50) 