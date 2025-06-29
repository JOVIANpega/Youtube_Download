#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import traceback
import ssl
import subprocess
import platform

# 設置環境變數禁用 yt-dlp 更新
os.environ["YTDLP_NO_UPDATE"] = "1"

# 添加項目根目錄到 Python 路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 檢查 FFmpeg 是否存在
def check_ffmpeg():
    ffmpeg_bin_dir = os.path.join(current_dir, "ffmpeg_bin")
    ffmpeg_exe = os.path.join(ffmpeg_bin_dir, "ffmpeg.exe")
    
    if os.path.exists(ffmpeg_exe):
        print(f"找到 FFmpeg: {ffmpeg_exe}")
        # 設置環境變數，確保 yt-dlp 可以找到 FFmpeg
        os.environ["PATH"] = ffmpeg_bin_dir + os.pathsep + os.environ.get("PATH", "")
        os.environ["FFMPEG_LOCATION"] = ffmpeg_exe
        return True
    else:
        print("未找到 FFmpeg，將嘗試自動下載")
        return False

# 檢查 FFmpeg
check_ffmpeg()

# 添加異常處理
try:
    # 應用 SSL 修復
    from src.ssl_fix import apply_ssl_fix, check_ytdlp_version, test_youtube_connection
    print("正在應用 SSL 修復...")
    apply_ssl_fix()
    
    # 檢查 yt-dlp 版本
    print("檢查 yt-dlp 版本...")
    check_ytdlp_version()
    
    # 測試 YouTube 連接
    print("測試 YouTube 連接...")
    test_youtube_connection()
    
    # 導入必要的模組
    import PySide6
    from PySide6.QtWidgets import QApplication
    import yt_dlp
    
    # 確保 user_preferences.py 可以被找到
    from src.user_preferences import UserPreferences
    
    # 導入主視窗
    from src.ui.main_window_pyside import MainWindow
    
    def main():
        # 創建應用程式實例
        app = QApplication(sys.argv)
        
        # 創建主視窗
        window = MainWindow()
        window.show()
        
        # 執行應用程式
        sys.exit(app.exec())
    
    if __name__ == "__main__":
        main()

except Exception as e:
    # 捕獲並記錄異常
    error_msg = f"啟動時發生錯誤: {str(e)}\n{traceback.format_exc()}"
    
    # 寫入錯誤日誌
    with open("error_log.txt", "w", encoding="utf-8") as f:
        f.write(error_msg)
    
    # 嘗試顯示錯誤對話框
    try:
        from PySide6.QtWidgets import QApplication, QMessageBox
        app = QApplication(sys.argv)
        QMessageBox.critical(None, "啟動錯誤", f"程式啟動失敗，錯誤信息已保存到 error_log.txt\n\n錯誤: {str(e)}")
    except:
        # 如果無法顯示 GUI 錯誤，則輸出到控制台
        print(error_msg)
    
    sys.exit(1) 