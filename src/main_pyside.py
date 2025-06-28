#!/usr/bin/env python3
"""
YouTube 下載器主程式 (PySide6 版本)
YouTube Downloader Main Program (PySide6 Version)
YouTubeダウンローダーメインプログラム (PySide6版)
유튜브 다운로더 메인 프로그램 (PySide6 버전)
"""

import sys
import os
import ssl
import certifi

# 修復 SSL 證書問題
def fix_ssl_issues():
    """修復 SSL 證書問題"""
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 設定全域 SSL 上下文
        ssl._create_default_https_context = lambda: ssl_context
        
        print("✓ SSL 證書問題已修復")
        return True
        
    except Exception as e:
        print(f"✗ SSL 修復失敗: {e}")
        return False

# 在導入其他模組前先修復 SSL
fix_ssl_issues()

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window_pyside import MainWindow
from PySide6.QtWidgets import QApplication

ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

def main():
    """主函數"""
    app = QApplication(sys.argv)
    
    # 設定應用程式資訊
    app.setApplicationName("YouTube 下載器")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("YouTube Downloader")
    
    # 創建主視窗
    window = MainWindow()
    window.show()
    
    # 運行應用程式
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 