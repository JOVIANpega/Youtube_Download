#!/usr/bin/env python3
"""
YouTube 下載器啟動腳本 (改進版)
Enhanced YouTube Downloader Launcher
改良されたYouTubeダウンローダー起動スクリプト
개선된 유튜브 다운로더 실행 스크립트
"""

import sys
import os
import subprocess

def install_dependencies():
    """安裝必要的依賴"""
    print("檢查並安裝依賴...")
    
    dependencies = [
        "certifi",
        "PySide6",
        "yt-dlp"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            print(f"✓ {dep} 已安裝")
        except ImportError:
            print(f"正在安裝 {dep}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                print(f"✓ {dep} 安裝成功")
            except Exception as e:
                print(f"✗ {dep} 安裝失敗: {e}")
                return False
    
    return True

def fix_ssl_issues():
    """修復 SSL 問題"""
    print("修復 SSL 證書問題...")
    
    try:
        import ssl
        import certifi
        
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 設定全域 SSL 上下文
        ssl._create_default_https_context = lambda: ssl_context
        
        print("✓ SSL 問題已修復")
        return True
        
    except Exception as e:
        print(f"✗ SSL 修復失敗: {e}")
        return False

def run_gui():
    """運行 GUI 版本"""
    print("啟動 GUI 版本...")
    
    try:
        # 先修復 SSL 問題
        fix_ssl_issues()
        
        # 導入並運行主程式
        from src.ui.main_window_pyside import MainWindow
        from PySide6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"GUI 啟動失敗: {e}")
        return False

def run_cli():
    """運行命令行版本"""
    print("啟動命令行版本...")
    
    try:
        # 先修復 SSL 問題
        fix_ssl_issues()
        
        # 運行命令行版本
        os.system(f"{sys.executable} src/cli_downloader.py")
        return True
        
    except Exception as e:
        print(f"CLI 啟動失敗: {e}")
        return False

def main():
    print("YouTube 下載器啟動器 (改進版)")
    print("=" * 50)
    
    # 檢查並安裝依賴
    if not install_dependencies():
        print("依賴安裝失敗，請手動安裝")
        return
    
    # 檢查命令行參數
    if len(sys.argv) > 1:
        if sys.argv[1] == "cli":
            run_cli()
        elif sys.argv[1] == "gui":
            run_gui()
        else:
            print("無效參數，使用預設 GUI 模式")
            run_gui()
        return
    
    # 互動式選擇
    print("\n選擇啟動模式:")
    print("1. GUI 模式 (圖形介面)")
    print("2. 命令行模式")
    print("3. 退出")
    
    while True:
        try:
            choice = input("\n請選擇 (1-3): ").strip()
            
            if choice == "1":
                run_gui()
                break
            elif choice == "2":
                run_cli()
                break
            elif choice == "3":
                print("再見！")
                break
            else:
                print("無效選擇，請重新輸入")
                
        except KeyboardInterrupt:
            print("\n\n再見！")
            break
        except Exception as e:
            print(f"發生錯誤: {e}")

if __name__ == "__main__":
    main() 