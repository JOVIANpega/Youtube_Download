#!/usr/bin/env python3
"""
YouTube 下載器啟動腳本
YouTube Downloader Launcher
YouTubeダウンローダー起動スクリプト
유튜브 다운로더 실행 스크립트
"""

import sys
import os

def check_gui_available():
    """檢查 GUI 是否可用"""
    try:
        # 嘗試 PySide6
        import PySide6
        return "PySide6"
    except ImportError:
        try:
            # 嘗試 PyQt6
            import PyQt6
            return "PyQt6"
        except ImportError:
            return None

def main():
    print("YouTube 下載器啟動器")
    print("=" * 50)
    
    # 檢查是否有命令行參數
    if len(sys.argv) > 1:
        # 直接使用命令行版本
        print("使用命令行模式...")
        os.system(f"python src/cli_downloader.py {' '.join(sys.argv[1:])}")
        return
    
    # 檢查 GUI 可用性
    gui_type = check_gui_available()
    
    if gui_type:
        print(f"✓ 檢測到 {gui_type}，可以使用 GUI 模式")
        print("\n選擇啟動模式:")
        print("1. GUI 模式 (圖形介面)")
        print("2. 命令行模式")
        print("3. 退出")
        
        while True:
            choice = input("\n請選擇 (1-3): ").strip()
            
            if choice == "1":
                print("啟動 GUI 模式...")
                if gui_type == "PySide6":
                    os.system("python src/main_pyside.py")
                else:
                    os.system("python src/main.py")
                break
            elif choice == "2":
                print("啟動命令行模式...")
                print("請輸入 YouTube URL:")
                url = input("URL: ").strip()
                if url:
                    os.system(f"python src/cli_downloader.py \"{url}\"")
                break
            elif choice == "3":
                print("再見！")
                break
            else:
                print("無效選擇，請重新輸入")
    else:
        print("⚠️  未檢測到 GUI 庫，使用命令行模式")
        print("請輸入 YouTube URL:")
        url = input("URL: ").strip()
        if url:
            os.system(f"python src/cli_downloader.py \"{url}\"")
        else:
            print("未提供 URL，退出")

if __name__ == "__main__":
    main() 