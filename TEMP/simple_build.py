#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單打包腳本 - YouTube 影片下載器 V1.4
"""

import os
import sys
import subprocess
from datetime import datetime

def main():
    print("=" * 60)
    print("YouTube 影片下載器 V1.4 簡單打包腳本")
    print("=" * 60)
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查PyInstaller是否已安裝
    try:
        import PyInstaller
        print("✅ PyInstaller 已安裝")
    except ImportError:
        print("❌ PyInstaller 未安裝，正在安裝...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 打包命令
    cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", "YouTube下載器V1.4",
        "src/main_pyside.py"
    ]
    
    print("執行打包命令:", " ".join(cmd))
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ 打包成功！")
        
        # 創建 dist 目錄（如果不存在）
        os.makedirs("dist", exist_ok=True)
        
        # 複製版本和說明文件到發布目錄
        if os.path.exists("VERSION"):
            with open("VERSION", "r", encoding="utf-8") as f_src:
                with open("dist/VERSION.txt", "w", encoding="utf-8") as f_dst:
                    f_dst.write(f_src.read())
            print("✅ 版本文件已複製")
        
        if os.path.exists("高解析度下載功能改進說明.md"):
            with open("高解析度下載功能改進說明.md", "r", encoding="utf-8") as f_src:
                with open("dist/高解析度下載功能改進說明.txt", "w", encoding="utf-8") as f_dst:
                    f_dst.write(f_src.read())
            print("✅ 功能說明已複製")
        
        if os.path.exists("RELEASE_NOTES_V1.4.md"):
            with open("RELEASE_NOTES_V1.4.md", "r", encoding="utf-8") as f_src:
                with open("dist/發布說明.txt", "w", encoding="utf-8") as f_dst:
                    f_dst.write(f_src.read())
            print("✅ 發布說明已複製")
        
        # 創建簡單的說明文件
        with open("dist/使用說明.txt", "w", encoding="utf-8") as f:
            f.write("YouTube 影片下載器 V1.4 - 高解析度支援版本\n")
            f.write("=" * 50 + "\n\n")
            f.write("使用方法：\n")
            f.write("1. 執行 YouTube下載器V1.4.exe\n")
            f.write("2. 輸入 YouTube 影片網址\n")
            f.write("3. 點擊「獲取資訊」按鈕\n")
            f.write("4. 選擇解析度（例如「最高品質」或「1080P (Full HD)」）\n")
            f.write("5. 點擊「開始下載」按鈕\n\n")
            f.write("新功能：\n")
            f.write("- 強化高解析度下載支援\n")
            f.write("- 改進合併失敗處理，保留已下載檔案\n")
            f.write("- 多層備用下載策略\n")
            f.write("- 前綴歷史記錄功能\n")
            f.write("- 檢查更新按鈕\n\n")
        print("✅ 使用說明已創建")
        
        print("✅ 所有文件已準備完成")
    else:
        print("❌ 打包失敗")
    
    print("=" * 60)
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main() 