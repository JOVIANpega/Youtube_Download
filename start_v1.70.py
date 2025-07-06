#!/usr/bin/env python3
"""
多平台影片下載器 V1.70
Multi-platform Video Downloader V1.70
マルチプラットフォーム動画ダウンローダー V1.70
멀티 플랫폼 비디오 다운로더 V1.70
"""

import os
import sys
import subprocess
import traceback
import importlib.util
import time

# 設置工作目錄
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 將 src 目錄添加到 Python 路徑
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
sys.path.insert(0, src_path)

# 檢查 yt-dlp 是否已安裝
def check_ytdlp():
    try:
        import yt_dlp
        return True
    except ImportError:
        return False

# 安裝 yt-dlp
def install_ytdlp():
    print("正在安裝 yt-dlp...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])

# 安全等待用戶輸入
def safe_input(prompt):
    """安全的輸入函數，避免在PyInstaller打包後出現stdin錯誤"""
    try:
        return input(prompt)
    except Exception as e:
        print(f"{prompt} (按Enter繼續...)")
        try:
            # 等待幾秒鐘
            time.sleep(5)
            return ""
        except Exception:
            return ""

# 主程式
def main():
    # 檢查並安裝 yt-dlp
    if not check_ytdlp():
        install_ytdlp()
    
    print("正在啟動多平台影片下載器 V1.70...")
    
    # 導入主程式
    try:
        # 確保src目錄在路徑中
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # 使用importlib動態導入模組
        tabbed_gui_path = os.path.join(src_path, "tabbed_gui_demo.py")
        if os.path.exists(tabbed_gui_path):
            # 使用importlib.util.spec_from_file_location動態導入模組
            spec = importlib.util.spec_from_file_location("tabbed_gui_demo", tabbed_gui_path)
            tabbed_gui = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tabbed_gui)
            
            # 執行main函數
            if hasattr(tabbed_gui, 'main'):
                tabbed_gui.main()
            else:
                print("錯誤: tabbed_gui_demo.py 中找不到 main 函數")
                safe_input("按 Enter 鍵退出...")
        else:
            print(f"錯誤: 找不到文件 {tabbed_gui_path}")
            safe_input("按 Enter 鍵退出...")
    except Exception as e:
        print(f"啟動失敗: {str(e)}")
        print("堆疊追蹤:")
        traceback.print_exc()
        safe_input("按 Enter 鍵退出...")

if __name__ == "__main__":
    main() 