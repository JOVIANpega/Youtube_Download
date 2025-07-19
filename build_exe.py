#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多平台影片下載器 EXE 打包腳本
使用 PyInstaller 打包為單一執行檔
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("=== 多平台影片下載器 EXE 打包工具 ===")
    
    # 檢查必要檔案
    main_script = "src/tabbed_gui_demo.py"
    if not os.path.exists(main_script):
        print(f"錯誤：找不到主程式檔案 {main_script}")
        return False
    
    # 創建 assets 目錄（如果不存在）
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        print(f"已創建 {assets_dir} 目錄")
    
    # 創建圖示檔案（如果不存在）
    icon_path = os.path.join(assets_dir, "icon.ico")
    if not os.path.exists(icon_path):
        print(f"警告：找不到圖示檔案 {icon_path}")
        print("將使用預設圖示")
        icon_path = None
    
    # 清理舊的打包檔案
    dist_dir = "dist"
    build_dir = "build"
    spec_file = "tabbed_gui_demo.spec"
    
    for path in [dist_dir, build_dir]:
        if os.path.exists(path):
            print(f"清理 {path} 目錄...")
            shutil.rmtree(path)
    
    if os.path.exists(spec_file):
        print(f"刪除舊的 {spec_file}...")
        os.remove(spec_file)
    
    # 構建 PyInstaller 命令
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包為單一檔案
        "--noconsole",                  # 不顯示控制台視窗
        "--name=多平台影片下載器",        # 設定執行檔名稱
        "--clean",                      # 清理快取
        "--distpath=dist",              # 輸出目錄
        "--workpath=build",             # 工作目錄
        "--add-data=src/progress_tab.py;."  # 添加進度標籤頁模組
    ]
    
    # 添加圖示（如果存在）
    if icon_path and os.path.exists(icon_path):
        cmd.extend(["--icon", icon_path])
    
    # 添加主程式
    cmd.append(main_script)
    
    print("開始打包...")
    print(f"執行命令: {' '.join(cmd)}")
    
    try:
        # 執行 PyInstaller
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("打包成功！")
        
        # 檢查輸出檔案
        exe_path = os.path.join(dist_dir, "多平台影片下載器.exe")
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"執行檔已生成：{exe_path}")
            print(f"檔案大小：{file_size:.1f} MB")
            
            # 複製 setup.json 到 dist 目錄（如果存在）
            setup_json = "src/setup.json"
            if os.path.exists(setup_json):
                dist_setup = os.path.join(dist_dir, "setup.json")
                shutil.copy2(setup_json, dist_setup)
                print(f"已複製設定檔到：{dist_setup}")
            
            print("\n=== 打包完成 ===")
            print(f"執行檔位置：{os.path.abspath(exe_path)}")
            print("您可以直接執行此檔案來啟動下載器")
            return True
        else:
            print("錯誤：找不到生成的執行檔")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"打包失敗：{e}")
        print(f"錯誤輸出：{e.stderr}")
        return False
    except Exception as e:
        print(f"打包過程中發生錯誤：{e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n打包失敗，請檢查錯誤訊息")
        sys.exit(1)
    else:
        print("\n打包成功完成！") 