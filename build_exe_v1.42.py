#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 影片下載器 V1.42 打包腳本
"""

import os
import sys
import shutil
import subprocess
import platform
from datetime import datetime

def main():
    print("=" * 60)
    print("YouTube 影片下載器 V1.42 打包腳本")
    print("高解析度支援版本 + 文字大小調整功能 + 紅綠色文字顯示")
    print("=" * 60)
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"系統: {platform.system()} {platform.release()}")
    print(f"Python版本: {platform.python_version()}")
    print("=" * 60)
    
    # 檢查PyInstaller是否已安裝
    try:
        import PyInstaller
        print("✅ PyInstaller 已安裝")
    except ImportError:
        print("❌ PyInstaller 未安裝，正在安裝...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 確保版本文件存在
    if not os.path.exists("VERSION"):
        print("❌ 找不到 VERSION 文件")
        return
    
    # 確保版本信息文件存在
    if not os.path.exists("version_info.txt"):
        print("❌ 找不到 version_info.txt 文件")
        return
    
    # 清理舊的構建文件
    if os.path.exists("build"):
        print("清理舊的構建文件...")
        shutil.rmtree("build", ignore_errors=True)
    
    if os.path.exists("dist"):
        print("清理舊的發布文件...")
        shutil.rmtree("dist", ignore_errors=True)
    
    # 創建輸出目錄
    os.makedirs("dist", exist_ok=True)
    
    # 打包命令
    cmd = [
        sys.executable, 
        "-m", 
        "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", "YouTube下載器V1.42",
        "--version-file", "version_info.txt",
        "--add-data", "VERSION;.",
        "src/main_pyside.py"
    ]
    
    print("執行打包命令:", " ".join(cmd))
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("✅ 打包成功！")
        output_path = os.path.abspath("dist/YouTube下載器V1.42.exe")
        print(f"輸出文件: {output_path}")
        
        # 複製版本和說明文件到發布目錄
        shutil.copy("VERSION", "dist/VERSION")
        if os.path.exists("高解析度下載功能改進說明.md"):
            shutil.copy("高解析度下載功能改進說明.md", "dist/高解析度下載功能改進說明.md")
        
        # 創建簡單的說明文件
        with open("dist/使用說明.txt", "w", encoding="utf-8") as f:
            f.write("YouTube 影片下載器 V1.42 - 高解析度支援版本\n")
            f.write("=" * 50 + "\n\n")
            f.write("使用方法：\n")
            f.write("1. 執行 YouTube下載器V1.42.exe\n")
            f.write("2. 輸入 YouTube 影片網址\n")
            f.write("3. 點擊「獲取資訊」按鈕\n")
            f.write("4. 選擇解析度（例如「最高品質」或「1080P (Full HD)」）\n")
            f.write("5. 點擊「開始下載」按鈕\n\n")
            f.write("新功能：\n")
            f.write("- 強化高解析度下載支援\n")
            f.write("- 改進合併失敗處理，保留已下載檔案\n")
            f.write("- 多層備用下載策略\n")
            f.write("- 前綴歷史記錄功能\n")
            f.write("- 檢查更新按鈕\n")
            f.write("- 文字大小調整功能\n")
            f.write("- 紅綠色文字顯示\n\n")
            f.write("詳細說明請參考「高解析度下載功能改進說明.md」\n")
        
        # 創建發布說明文件
        with open("dist/發布說明.txt", "w", encoding="utf-8") as f:
            f.write("YouTube 影片下載器 V1.42 發布說明\n")
            f.write("=" * 50 + "\n\n")
            f.write("版本: V1.42\n")
            f.write("發布日期: 2024-12-30\n\n")
            f.write("新增功能:\n")
            f.write("1. 文字大小調整功能 - 可透過 + 和 - 按鈕調整日誌文字大小\n")
            f.write("2. 紅綠色文字顯示 - 錯誤訊息以紅色顯示，成功訊息以綠色顯示\n")
            f.write("3. 修復下載完成提醒視窗選項問題\n\n")
            f.write("改進:\n")
            f.write("1. 優化介面文字預設大小為 11pt\n")
            f.write("2. 修復完整路徑前的圖標顯示問題\n")
            f.write("3. 移除可能顯示異常的 Unicode 圖標\n\n")
            f.write("詳細說明請參考「高解析度下載功能改進說明.md」\n")
        
        print("✅ 附加文件已複製到發布目錄")
    else:
        print("❌ 打包失敗")
    
    print("=" * 60)
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main() 