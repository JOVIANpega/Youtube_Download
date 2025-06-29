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
import subprocess
import threading
import json
import time
import urllib.request
import pkg_resources

from PySide6.QtWidgets import QApplication, QMessageBox

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

# 檢查 yt-dlp 版本
def check_ytdlp_version():
    """檢查 yt-dlp 版本，如果有新版本則返回新版本號，否則返回 None"""
    try:
        # 獲取當前版本
        try:
            current_version = pkg_resources.get_distribution("yt-dlp").version
        except pkg_resources.DistributionNotFound:
            print("yt-dlp 未安裝")
            return None
        
        print(f"當前 yt-dlp 版本: {current_version}")
        
        # 檢查網絡連接
        try:
            # 嘗試連接到 PyPI API
            urllib.request.urlopen("https://pypi.org/pypi/yt-dlp/json", timeout=3)
        except:
            print("無法連接到網絡，跳過版本檢查")
            return None
        
        # 獲取最新版本
        try:
            with urllib.request.urlopen("https://pypi.org/pypi/yt-dlp/json") as response:
                data = json.loads(response.read().decode())
                latest_version = data["info"]["version"]
                print(f"最新 yt-dlp 版本: {latest_version}")
                
                # 比較版本
                if latest_version != current_version:
                    return latest_version
        except Exception as e:
            print(f"檢查版本時出錯: {e}")
            
        return None
    except Exception as e:
        print(f"版本檢查過程中出錯: {e}")
        return None

# 更新 yt-dlp
def update_ytdlp():
    """更新 yt-dlp 到最新版本"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"])
        return True
    except Exception as e:
        print(f"更新 yt-dlp 失敗: {e}")
        return False

# 在導入其他模組前先修復 SSL
fix_ssl_issues()

# 添加 src 目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

def show_update_dialog(app, latest_version):
    """顯示更新對話框"""
    msg_box = QMessageBox()
    msg_box.setWindowTitle("yt-dlp 更新")
    msg_box.setText(f"發現 yt-dlp 新版本: {latest_version}\n是否要更新？")
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.Yes)
    
    if msg_box.exec() == QMessageBox.Yes:
        # 顯示更新中的訊息
        updating_msg = QMessageBox()
        updating_msg.setWindowTitle("更新中")
        updating_msg.setText("正在更新 yt-dlp，請稍候...")
        updating_msg.setStandardButtons(QMessageBox.NoButton)
        
        # 使用線程進行更新，避免凍結UI
        def update_thread():
            success = update_ytdlp()
            updating_msg.done(0)
            
            # 顯示更新結果
            result_msg = QMessageBox()
            if success:
                result_msg.setWindowTitle("更新成功")
                result_msg.setText(f"yt-dlp 已成功更新到版本 {latest_version}")
            else:
                result_msg.setWindowTitle("更新失敗")
                result_msg.setText("yt-dlp 更新失敗，請手動更新")
            result_msg.setStandardButtons(QMessageBox.Ok)
            result_msg.exec()
        
        # 啟動更新線程
        threading.Thread(target=update_thread).start()
        updating_msg.exec()

def main():
    """主函數"""
    app = QApplication(sys.argv)
    
    # 設定應用程式資訊
    app.setApplicationName("YouTube 下載器")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("YouTube Downloader")
    
    # 在背景線程中檢查 yt-dlp 版本
    def version_check_thread():
        time.sleep(1)  # 延遲一秒，讓主視窗先顯示
        latest_version = check_ytdlp_version()
        if latest_version:
            app.processEvents()  # 確保UI響應
            show_update_dialog(app, latest_version)
    
    # 啟動版本檢查線程
    threading.Thread(target=version_check_thread).start()
    
    # 創建主視窗
    from ui.main_window_pyside import MainWindow
    window = MainWindow()
    window.show()
    
    # 運行應用程式
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 