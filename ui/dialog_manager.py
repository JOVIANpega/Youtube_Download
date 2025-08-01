#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
對話框管理器
處理各種彈窗和用戶交互
"""

import os
import subprocess
import platform
from PySide6.QtWidgets import (
    QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QTextEdit, QDialogButtonBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QPixmap

from logger import logger

class DialogManager:
    """對話框管理器"""
    
    @staticmethod
    def show_download_error(parent, error_message, url="", suggestions=None):
        """顯示下載錯誤對話框"""
        dialog = QMessageBox(parent)
        dialog.setWindowTitle("下載失敗")
        dialog.setIcon(QMessageBox.Warning)
        
        # 主要錯誤訊息
        main_text = f"❌ 影片下載失敗\n\n錯誤原因：\n{error_message}"
        
        if url:
            main_text += f"\n\nURL：{url}"
        
        dialog.setText(main_text)
        
        # 建議和解決方案
        if suggestions:
            detail_text = "💡 建議解決方案：\n\n"
            for i, suggestion in enumerate(suggestions, 1):
                detail_text += f"{i}. {suggestion}\n"
            dialog.setDetailedText(detail_text)
        
        # 添加按鈕
        dialog.setStandardButtons(QMessageBox.Ok)
        
        # 如果有替代下載方案，添加額外按鈕
        if "年齡驗證" in error_message or "登入" in error_message:
            dialog.addButton("嘗試其他方式", QMessageBox.ActionRole)
        
        dialog.exec()
        return dialog.clickedButton()
    
    @staticmethod
    def show_download_success(parent, file_path, file_name):
        """顯示下載成功對話框"""
        dialog = QMessageBox(parent)
        dialog.setWindowTitle("下載完成")
        dialog.setIcon(QMessageBox.Information)
        
        # 主要訊息
        main_text = f"✅ 影片下載成功！\n\n檔案名稱：{file_name}"
        
        # 檔案資訊
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            size_mb = size / 1024 / 1024
            main_text += f"\n檔案大小：{size_mb:.1f} MB"
            main_text += f"\n儲存位置：{os.path.dirname(file_path)}"
        
        dialog.setText(main_text)
        
        # 自定義按鈕
        play_button = dialog.addButton("🎬 播放影片", QMessageBox.ActionRole)
        folder_button = dialog.addButton("📁 打開目錄", QMessageBox.ActionRole)
        close_button = dialog.addButton("關閉", QMessageBox.RejectRole)
        
        dialog.exec()
        clicked = dialog.clickedButton()
        
        if clicked == play_button:
            DialogManager.play_video(file_path)
        elif clicked == folder_button:
            DialogManager.open_folder(file_path)
        
        return clicked
    
    @staticmethod
    def play_video(file_path):
        """播放影片"""
        try:
            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", file_path])
            logger.info(f"開始播放影片: {file_path}")
        except Exception as e:
            logger.error(f"播放影片失敗: {str(e)}")
    
    @staticmethod
    def open_folder(file_path):
        """打開檔案所在目錄"""
        try:
            folder_path = os.path.dirname(file_path)
            if platform.system() == "Windows":
                subprocess.run(["explorer", "/select,", file_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", "-R", file_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
            logger.info(f"打開目錄: {folder_path}")
        except Exception as e:
            logger.error(f"打開目錄失敗: {str(e)}")
    
    @staticmethod
    def show_alternative_download(parent, platform_name, url):
        """顯示替代下載方案對話框"""
        dialog = QDialog(parent)
        dialog.setWindowTitle(f"{platform_name} 替代下載方案")
        dialog.setModal(True)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 標題
        title_label = QLabel(f"⚠️ {platform_name} 平台需要特殊處理")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #e67e22;")
        layout.addWidget(title_label)
        
        # 說明文字
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(200)
        
        if "年齡驗證" in platform_name or "YouTube" in platform_name:
            content = """
🔍 問題說明：
此影片需要年齡驗證，必須登入YouTube帳號才能下載。

💡 建議解決方案：

1. 【瀏覽器下載】
   - 使用瀏覽器登入YouTube
   - 複製影片URL到線上下載工具
   - 推薦：y2mate.com, savefrom.net

2. 【更換影片】
   - 尋找相同內容但無年齡限制的影片
   - 選擇其他創作者的類似影片

3. 【專用工具】
   - 使用支援Cookie的下載工具
   - 4K Video Downloader
   - JDownloader 2

4. 【手機下載】
   - 使用手機YouTube應用
   - 下載到手機後傳輸到電腦
            """
        else:
            content = f"""
🔍 問題說明：
{platform_name} 平台需要登入才能下載影片。

💡 建議解決方案：

1. 【瀏覽器下載】
   - 登入{platform_name}官網
   - 使用瀏覽器擴充功能下載

2. 【線上工具】
   - 使用支援{platform_name}的線上下載工具
   - 注意：某些工具可能需要登入

3. 【專用軟體】
   - 使用支援多平台的下載軟體
   - 配置帳號登入資訊
            """
        
        info_text.setPlainText(content.strip())
        layout.addWidget(info_text)
        
        # 按鈕
        button_layout = QHBoxLayout()
        
        browser_button = QPushButton("🌐 開啟瀏覽器")
        browser_button.clicked.connect(lambda: DialogManager.open_browser(url))
        
        copy_button = QPushButton("📋 複製URL")
        copy_button.clicked.connect(lambda: DialogManager.copy_to_clipboard(url))
        
        close_button = QPushButton("關閉")
        close_button.clicked.connect(dialog.accept)
        
        button_layout.addWidget(browser_button)
        button_layout.addWidget(copy_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    @staticmethod
    def open_browser(url):
        """在瀏覽器中打開URL"""
        try:
            import webbrowser
            webbrowser.open(url)
            logger.info(f"在瀏覽器中打開: {url}")
        except Exception as e:
            logger.error(f"打開瀏覽器失敗: {str(e)}")
    
    @staticmethod
    def copy_to_clipboard(text):
        """複製文字到剪貼板"""
        try:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            logger.info(f"已複製到剪貼板: {text}")
        except Exception as e:
            logger.error(f"複製到剪貼板失敗: {str(e)}")
    
    @staticmethod
    def show_settings_saved(parent):
        """顯示設定已保存訊息"""
        QMessageBox.information(
            parent,
            "設定已保存",
            "✅ 所有設定已成功保存到 setup.json\n\n設定將在下次啟動時自動載入。"
        )
    
    @staticmethod
    def confirm_reset_settings(parent):
        """確認重置設定"""
        reply = QMessageBox.question(
            parent,
            "重置設定",
            "⚠️ 確定要重置所有設定為預設值嗎？\n\n這將清除：\n• 下載路徑\n• 檔名前綴\n• 字體大小\n• 視窗大小\n• 所有自定義設定\n\n此操作無法復原。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return reply == QMessageBox.Yes
