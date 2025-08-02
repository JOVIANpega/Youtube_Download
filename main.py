#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
YouTube下載器 v1.0.0 - 最終完整版
整合所有功能：下載、設定、彈窗、自動保存
"""

import sys
import os
from pathlib import Path

# 添加當前目錄到Python路徑
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QComboBox, QGroupBox, QCheckBox, QMessageBox,
    QScrollArea, QFormLayout, QSlider, QSpinBox, QFileDialog, QMenu
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont
import webbrowser

# 導入自定義模組
from enhanced_setup_manager import enhanced_setup_manager
from ui.dialog_manager import DialogManager
from download_thread import DownloadThread
from platform_detector import identify_platform
from logger import logger

class YouTubeDownloader(QWidget):
    """YouTube下載器主頁面"""
    
    download_started = Signal(str, str)  # URL, 檔案名
    
    def __init__(self):
        super().__init__()
        self.current_downloads = {}  # task_id -> thread
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 標題
        title = QLabel("📥 YouTube影片下載器")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # URL輸入區域 - 緊湊設計
        url_group = QGroupBox("🔗 影片網址")
        url_layout = QVBoxLayout(url_group)
        url_layout.setSpacing(4)  # 緊湊間距
        url_layout.setContentsMargins(8, 6, 8, 6)  # 緊湊邊距

        # URL輸入框 - 150字元寬度
        url_input_layout = QHBoxLayout()
        url_input_layout.setSpacing(4)  # 緊湊間距
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("請輸入影片網址...")
        self.url_edit.setMinimumHeight(28)
        self.url_edit.setMaxLength(150)  # 150字元限制
        self.url_edit.setMinimumWidth(600)  # 150字元寬度
        self.url_edit.setMaximumWidth(700)

        clear_btn = QPushButton("❌")
        clear_btn.setMaximumWidth(28)
        clear_btn.setMaximumHeight(28)
        clear_btn.setToolTip("清除網址輸入框")
        clear_btn.clicked.connect(lambda: self.url_edit.clear())

        url_input_layout.addWidget(self.url_edit)
        url_input_layout.addWidget(clear_btn)
        url_layout.addLayout(url_input_layout)

        # 支援平台提示 - 受字體大小控制
        platform_label = QLabel("✅ 支援：YouTube、Bilibili、TikTok、QQ影片等1000+網站")
        platform_label.setStyleSheet("color: #27ae60; margin: 1px; padding: 2px;")  # 移除固定字體大小
        url_layout.addWidget(platform_label)

        layout.addWidget(url_group)
        
        # 下載設定區域 - 緊湊設計
        settings_group = QGroupBox("⚙️ 下載設定")
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(4)  # 更緊湊間距
        settings_layout.setContentsMargins(8, 8, 8, 8)  # 緊湊邊距

        # 第一行：路徑和前綴 - 水平緊湊排列
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(6)

        # 路徑部分
        path_label = QLabel("路徑:")
        path_label.setMinimumWidth(35)
        path_label.setMaximumWidth(35)
        self.path_edit = QLineEdit()
        self.path_edit.setMaxLength(150)  # 150字元限制
        self.path_edit.setMinimumHeight(24)
        self.path_edit.setMinimumWidth(300)  # 縮短以騰出空間
        self.path_edit.setMaximumWidth(350)
        self.path_edit.setToolTip("設定下載目錄路徑，最多150個字元")
        browse_btn = QPushButton("瀏覽")
        browse_btn.setMaximumWidth(40)
        browse_btn.setMaximumHeight(24)
        browse_btn.setToolTip("選擇下載目錄")
        browse_btn.clicked.connect(self.browse_path)

        # 前綴部分
        prefix_label = QLabel("前綴:")
        prefix_label.setMinimumWidth(35)
        prefix_label.setMaximumWidth(35)

        self.prefix_combo = QComboBox()
        self.prefix_combo.setEditable(True)
        self.prefix_combo.setMaximumHeight(24)
        self.prefix_combo.setMinimumWidth(80)  # 20字元預留寬度
        self.prefix_combo.setMaximumWidth(100)
        self.prefix_combo.setToolTip("設定檔名前綴，最多15個字元")
        self.prefix_combo.lineEdit().setMaxLength(15)  # 15字元限制

        # 預設前綴選項
        prefix_options = ["", "per-", "vid-", "dl-", "yt-", "new-", "test-"]
        self.prefix_combo.addItems(prefix_options)
        self.prefix_combo.setCurrentText(enhanced_setup_manager.get("filename_prefix", ""))
        self.prefix_combo.currentTextChanged.connect(self.on_prefix_changed)

        self.prefix_count = QLabel("0/15")
        self.prefix_count.setStyleSheet("color: #666;")
        self.prefix_count.setMinimumWidth(25)
        self.prefix_count.setMaximumWidth(25)

        # 組合第一行
        first_row_layout.addWidget(path_label)
        first_row_layout.addWidget(self.path_edit, 1)
        first_row_layout.addWidget(browse_btn)
        first_row_layout.addWidget(prefix_label)
        first_row_layout.addWidget(self.prefix_combo)
        first_row_layout.addWidget(self.prefix_count)
        settings_layout.addLayout(first_row_layout)

        # 第二行：品質、解析度和選項 - 水平緊湊排列
        second_row_layout = QHBoxLayout()
        second_row_layout.setSpacing(6)

        quality_label = QLabel("品質:")
        quality_label.setMinimumWidth(35)
        quality_label.setMaximumWidth(35)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["最高", "高品質", "中等", "音頻"])
        self.quality_combo.setMaximumHeight(24)
        self.quality_combo.setMinimumWidth(70)  # 20字元預留寬度
        self.quality_combo.setMaximumWidth(90)
        self.quality_combo.setToolTip("選擇影片品質等級")

        resolution_label = QLabel("解析度:")
        resolution_label.setMinimumWidth(50)
        resolution_label.setMaximumWidth(50)
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1080P", "720P", "480P", "360P", "自動"])
        self.resolution_combo.setMaximumHeight(24)
        self.resolution_combo.setMinimumWidth(70)  # 20字元預留寬度
        self.resolution_combo.setMaximumWidth(90)
        self.resolution_combo.setToolTip("選擇影片解析度")

        # 自動合併選項
        self.auto_merge_cb = QCheckBox("自動合併音視頻")
        self.auto_merge_cb.setChecked(True)
        self.auto_merge_cb.setToolTip("自動將音頻和視頻合併為單一檔案")

        # 組合第二行
        second_row_layout.addWidget(quality_label)
        second_row_layout.addWidget(self.quality_combo)
        second_row_layout.addWidget(resolution_label)
        second_row_layout.addWidget(self.resolution_combo)
        second_row_layout.addWidget(self.auto_merge_cb)
        second_row_layout.addStretch()
        settings_layout.addLayout(second_row_layout)
        
        layout.addWidget(settings_group)
        
        # 按鈕區域 - 水平布局
        button_layout = QHBoxLayout()

        # 下載按鈕 - 縮小版本
        self.download_btn = QPushButton("🚀 下載")
        self.download_btn.setMinimumHeight(35)
        self.download_btn.setMaximumWidth(100)  # 限制寬度
        self.download_btn.setToolTip("開始下載影片到指定目錄")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.download_btn.clicked.connect(self.start_download)

        # 外部工具按鈕
        self.external_tool_btn = QPushButton("🔗 外部工具")
        self.external_tool_btn.setMinimumHeight(35)
        self.external_tool_btn.setMaximumWidth(100)
        self.external_tool_btn.setToolTip("使用外部網站下載影片")
        self.external_tool_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:pressed {
                background-color: #a04000;
            }
        """)
        self.external_tool_btn.clicked.connect(self.show_external_tools)

        # 外部工具管理按鈕
        self.manage_tools_btn = QPushButton("⚙️ 管理")
        self.manage_tools_btn.setMinimumHeight(35)
        self.manage_tools_btn.setMaximumWidth(70)
        self.manage_tools_btn.setToolTip("管理外部下載工具列表")
        self.manage_tools_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #5d6d6e;
            }
        """)
        self.manage_tools_btn.clicked.connect(self.open_tools_manager)

        # 打開路徑按鈕
        self.open_folder_btn = QPushButton("📁 打開路徑")
        self.open_folder_btn.setMinimumHeight(35)
        self.open_folder_btn.setMaximumWidth(90)
        self.open_folder_btn.setToolTip("打開下載目錄")
        self.open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
        """)
        self.open_folder_btn.clicked.connect(self.open_download_folder)

        button_layout.addWidget(self.download_btn, 2)  # 下載按鈕佔2份
        button_layout.addWidget(self.external_tool_btn, 1)  # 外部工具按鈕佔1份
        button_layout.addWidget(self.manage_tools_btn, 1)  # 管理按鈕佔1份
        button_layout.addWidget(self.open_folder_btn, 1)  # 打開路徑按鈕佔1份
        layout.addLayout(button_layout)
        
        # 下載狀態區域 - 緊湊設計
        self.status_group = QGroupBox("📊 下載狀態")
        status_container_layout = QVBoxLayout(self.status_group)
        status_container_layout.setSpacing(4)
        status_container_layout.setContentsMargins(8, 8, 8, 8)

        # 清除所有按鈕 - 更小
        clear_all_layout = QHBoxLayout()
        self.clear_all_btn = QPushButton("🗑️ 清除")
        self.clear_all_btn.setMaximumHeight(24)
        self.clear_all_btn.setMaximumWidth(60)
        self.clear_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 2px 6px;
                font-size: 10px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        self.clear_all_btn.clicked.connect(self.clear_all_downloads)
        clear_all_layout.addStretch()
        clear_all_layout.addWidget(self.clear_all_btn)
        status_container_layout.addLayout(clear_all_layout)

        # 下載狀態列表 - 緊湊間距
        self.status_layout = QVBoxLayout()
        self.status_layout.setSpacing(2)
        status_container_layout.addLayout(self.status_layout)

        self.status_group.setVisible(False)
        layout.addWidget(self.status_group)

        # 下載狀態標籤字典
        self.status_labels = {}
        
        layout.addStretch()
    
    def load_settings(self):
        """載入設定"""
        self.path_edit.setText(enhanced_setup_manager.get("download_path", "M:/TEMP"))

        # 載入前綴設定
        saved_prefix = enhanced_setup_manager.get("filename_prefix", "per-")
        self.prefix_combo.setCurrentText(saved_prefix)

        # 載入前綴歷史
        prefix_history = enhanced_setup_manager.get("prefix_history", [])
        if prefix_history:
            # 清除現有項目並添加歷史項目
            self.prefix_combo.clear()
            # 先添加預設項目
            default_prefixes = ["per-", "per best-", "per best2-", "per best3-", "per nice-", "per nice2-"]
            all_prefixes = default_prefixes + [p for p in prefix_history if p not in default_prefixes]
            self.prefix_combo.addItems(all_prefixes)
            self.prefix_combo.setCurrentText(saved_prefix)

        self.quality_combo.setCurrentText(enhanced_setup_manager.get("format_option", "最高品質"))
        self.resolution_combo.setCurrentText(enhanced_setup_manager.get("resolution", "720P"))
        self.auto_merge_cb.setChecked(enhanced_setup_manager.get("auto_merge", True))
        self.on_prefix_changed()
    
    def save_settings(self):
        """保存設定"""
        enhanced_setup_manager.set("download_path", self.path_edit.text())

        # 保存前綴設定
        current_prefix = self.prefix_combo.currentText()
        enhanced_setup_manager.set("filename_prefix", current_prefix)

        # 保存前綴歷史
        prefix_history = enhanced_setup_manager.get("prefix_history", [])
        if current_prefix and current_prefix not in prefix_history:
            prefix_history.insert(0, current_prefix)
            # 限制歷史記錄數量
            prefix_history = prefix_history[:10]
            enhanced_setup_manager.set("prefix_history", prefix_history)

        enhanced_setup_manager.set("format_option", self.quality_combo.currentText())
        enhanced_setup_manager.set("resolution", self.resolution_combo.currentText())
        enhanced_setup_manager.set("auto_merge", self.auto_merge_cb.isChecked())
        enhanced_setup_manager.save_settings()
    
    def browse_path(self):
        """瀏覽下載路徑"""
        current_path = self.path_edit.text() or "M:/TEMP"
        path = QFileDialog.getExistingDirectory(self, "選擇下載路徑", current_path)
        if path:
            self.path_edit.setText(path)
            self.save_settings()
    
    def on_prefix_changed(self):
        """前綴變更處理"""
        text = self.prefix_combo.currentText()
        length = len(text)
        self.prefix_count.setText(f"{length}/15")

        if length > 15:
            self.prefix_count.setStyleSheet("color: red;")
        else:
            self.prefix_count.setStyleSheet("color: #666;")

        # 延遲保存設定，避免過於頻繁
        if hasattr(self, '_save_timer'):
            self._save_timer.stop()

        from PySide6.QtCore import QTimer
        self._save_timer = QTimer()
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self.save_settings)
        self._save_timer.start(500)  # 500ms後保存

    def show_external_tools(self):
        """顯示外部下載工具選單"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "提示", "請先輸入影片網址")
            return

        # 創建選單
        menu = QMenu(self)

        # 從設定中獲取外部工具列表
        external_tools = self.get_external_tools_from_settings(url)

        # 添加選單項目
        for tool in external_tools:
            action = menu.addAction(tool['name'])
            action.triggered.connect(lambda checked, url=tool['url']: self.open_external_tool(url))

        # 顯示選單
        menu.exec(self.external_tool_btn.mapToGlobal(self.external_tool_btn.rect().bottomLeft()))

    def open_external_tool(self, url):
        """打開外部工具"""
        try:
            webbrowser.open(url)
            logger.info(f"打開外部工具: {url}")
        except Exception as e:
            logger.error(f"打開外部工具失敗: {str(e)}")
            QMessageBox.warning(self, "錯誤", f"無法打開外部工具：{str(e)}")

    def get_external_tools_from_settings(self, url):
        """從設定中獲取外部工具列表"""
        tools_text = enhanced_setup_manager.get("external_tools", "")

        if not tools_text:
            # 如果沒有設定，使用預設值
            default_tools = [
                "🌐 SaveFrom.net|https://zh.savefrom.net/#{url}",
                "🎬 Y2Mate|https://www.y2mate.com/zh-cn/youtube/{url}",
                "📱 SnapSave|https://snapsave.app/zh?url={url}",
                "🔗 9xBuddy|https://9xbuddy.org/process?url={url}",
                "⚡ KeepVid|https://keepvid.com/?url={url}",
                "🎵 MP3 Converter|https://www.mp3converter.net/youtube-to-mp3/?url={url}",
                "📺 ClipConverter|https://www.clipconverter.cc/?url={url}",
                "🌟 Online Video Converter|https://www.onlinevideoconverter.com/zh/video-converter?url={url}"
            ]
            tools_text = "\n".join(default_tools)

        external_tools = []
        lines = [line.strip() for line in tools_text.split('\n') if line.strip()]

        for line in lines:
            if '|' in line:
                name, url_template = line.split('|', 1)
                tool_url = url_template.replace('{url}', url)
                external_tools.append({
                    'name': name.strip(),
                    'url': tool_url.strip()
                })

        return external_tools

    def open_tools_manager(self):
        """打開外部工具管理器"""
        try:
            from external_tools_manager import ExternalToolsManager
            manager = ExternalToolsManager(self)
            manager.tools_updated.connect(self.on_external_tools_updated)
            manager.exec()
        except Exception as e:
            logger.error(f"打開工具管理器失敗: {str(e)}")
            QMessageBox.warning(self, "錯誤", f"無法打開工具管理器：{str(e)}")

    def on_external_tools_updated(self):
        """外部工具更新後的處理"""
        logger.info("外部工具列表已更新")

    def safe_show_success_dialog(self, file_path, filename):
        """安全地顯示成功對話框"""
        try:
            DialogManager.show_download_success(self, file_path, filename)
        except Exception as e:
            logger.error(f"顯示成功對話框失敗: {str(e)}")

    def safe_remove_status_item(self, task_id):
        """安全地移除狀態項目"""
        try:
            self.remove_status_item(task_id)
        except Exception as e:
            logger.error(f"移除狀態項目失敗: {str(e)}")

    def open_download_folder(self):
        """打開下載目錄"""
        try:
            download_path = self.path_edit.text().strip()
            if not download_path:
                download_path = enhanced_setup_manager.get("download_path", "M:/TEMP")

            if not os.path.exists(download_path):
                QMessageBox.warning(self, "錯誤", f"目錄不存在：{download_path}")
                return

            import platform
            import subprocess

            if platform.system() == "Windows":
                subprocess.run(["explorer", download_path])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", download_path])
            else:  # Linux
                subprocess.run(["xdg-open", download_path])

            logger.info(f"打開下載目錄: {download_path}")
        except Exception as e:
            logger.error(f"打開目錄失敗: {str(e)}")
            QMessageBox.warning(self, "錯誤", f"無法打開目錄：{str(e)}")

    def start_fade_out_animation(self, task_id):
        """開始淡出動畫"""
        if task_id not in self.status_labels:
            return

        status_info = self.status_labels[task_id]
        container = status_info['container']

        # 創建透明度動畫
        self.fade_animation = QPropertyAnimation(container, b"windowOpacity")
        self.fade_animation.setDuration(2000)  # 2秒淡出
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        # 動畫完成後隱藏並清理
        self.fade_animation.finished.connect(lambda: self.remove_status_item(task_id))

        # 開始動畫
        self.fade_animation.start()

    def remove_status_item(self, task_id):
        """移除狀態項目"""
        if task_id in self.status_labels:
            status_info = self.status_labels[task_id]
            container = status_info['container']

            # 從布局中移除
            self.status_layout.removeWidget(container)
            container.deleteLater()

            # 從字典中移除
            del self.status_labels[task_id]

            # 如果沒有更多狀態，隱藏狀態組
            if not self.status_labels:
                self.status_group.setVisible(False)
    
    def start_download(self):
        """開始下載"""
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "錯誤", "請輸入影片網址！")
            return

        # 檢查是否已經在下載相同URL
        for task_id, thread in self.current_downloads.items():
            if hasattr(thread, 'url') and thread.url == url:
                QMessageBox.information(self, "提示", "此影片正在下載中，請等待完成！")
                return

        # 檢測平台
        platform_info = identify_platform(url)
        if not platform_info:
            DialogManager.show_download_error(
                self,
                "不支援的網址格式",
                url,
                ["請檢查網址是否正確", "確認是否為支援的平台"]
            )
            return

        # 檢查是否需要登入
        if platform_info.get('needs_login', False):
            DialogManager.show_alternative_download(self, platform_info['name'], url)
            return
        
        # 保存設定
        self.save_settings()
        
        # 創建下載線程
        thread = DownloadThread(
            url=url,
            output_path=self.path_edit.text(),
            format_option=self.quality_combo.currentText(),
            resolution=self.resolution_combo.currentText(),
            prefix=self.prefix_combo.currentText(),
            auto_merge=self.auto_merge_cb.isChecked()
        )
        
        thread.platform_info = platform_info
        
        # 連接信號
        thread.progress.connect(self.on_download_progress)
        thread.finished.connect(self.on_download_finished)
        
        # 開始下載
        task_id = f"task_{len(self.current_downloads)}"
        self.current_downloads[task_id] = thread
        
        # 顯示下載狀態
        self.show_download_status(task_id, platform_info['name'])
        
        # 啟動線程
        thread.start()
        
        # 發送信號
        self.download_started.emit(url, platform_info['name'])
        
        logger.info(f"開始下載: {url}")
    
    def show_download_status(self, task_id, platform_name):
        """顯示下載狀態 - 極簡版本"""
        # 創建狀態容器 - 極簡
        status_container = QWidget()
        status_container.setMaximumHeight(26)
        status_container_layout = QHBoxLayout(status_container)
        status_container_layout.setContentsMargins(2, 1, 2, 1)
        status_container_layout.setSpacing(3)

        # 狀態標籤 - 極簡
        status_label = QLabel(f"📥 {platform_name[:6]} 0%")  # 更短的平台名稱
        status_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 2px;
                padding: 2px 4px;
                color: #495057;
            }
        """)

        # 取消按鈕 - 極簡
        cancel_btn = QPushButton("×")
        cancel_btn.setMaximumWidth(20)
        cancel_btn.setMaximumHeight(20)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 2px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c82333; }
        """)
        cancel_btn.clicked.connect(lambda: self.cancel_download(task_id))

        status_container_layout.addWidget(status_label, 1)
        status_container_layout.addWidget(cancel_btn)

        self.status_labels[task_id] = {
            'container': status_container,
            'label': status_label,
            'cancel_btn': cancel_btn
        }

        self.status_layout.addWidget(status_container)
        self.status_group.setVisible(True)
    
    def on_download_progress(self, message, percent, speed, eta):
        """處理下載進度"""
        # 找到對應的狀態標籤並更新
        sender_thread = self.sender()

        for task_id, thread in self.current_downloads.items():
            if thread == sender_thread and task_id in self.status_labels:
                status_info = self.status_labels[task_id]
                if isinstance(status_info, dict) and 'label' in status_info:
                    # 極簡的進度顯示
                    speed_short = speed.replace("MiB/s", "M").replace("KiB/s", "K").replace("/s", "")
                    status_info['label'].setText(f"📥 {percent}% {speed_short}")
                break
    
    def on_download_finished(self, success, message, file_path):
        """處理下載完成"""
        try:
            # 找到完成的任務
            completed_task = None
            sender_thread = self.sender()

            for task_id, thread in self.current_downloads.items():
                if thread == sender_thread:
                    completed_task = task_id
                    break

            logger.info(f"下載完成處理: success={success}, task={completed_task}, file={file_path}")
        except Exception as e:
            logger.error(f"處理下載完成時發生錯誤: {str(e)}")
            return
        
        if completed_task:
            try:
                # 更新狀態標籤
                status_info = self.status_labels.get(completed_task)
                if status_info and isinstance(status_info, dict):
                    if success:
                        status_info['label'].setText(f"✅ 完成")
                        status_info['label'].setStyleSheet("""
                            QLabel {
                                background-color: #e8f5e8;
                                border: 1px solid #27ae60;
                                border-radius: 3px;
                                padding: 4px 6px;
                                margin: 1px;
                                color: #27ae60;
                            }
                        """)
                        # 隱藏取消按鈕
                        status_info['cancel_btn'].setVisible(False)

                        # 顯示完成對話框
                        if file_path and os.path.exists(file_path):
                            filename = os.path.basename(file_path)
                            # 確保在主線程中顯示對話框，使用變數捕獲避免閉包問題
                            from PySide6.QtCore import QTimer
                            QTimer.singleShot(100, lambda fp=file_path, fn=filename: self.safe_show_success_dialog(fp, fn))

                            # 彈出對話框後立即刪除下載狀態
                            QTimer.singleShot(200, lambda tid=completed_task: self.safe_remove_status_item(tid))

                        # 更新統計
                        if file_path and os.path.exists(file_path):
                            try:
                                file_size = os.path.getsize(file_path)
                                enhanced_setup_manager.update_statistics(True, file_size)
                                enhanced_setup_manager.save_settings()
                            except Exception as e:
                                logger.error(f"更新統計失敗: {str(e)}")
                    else:
                        # 下載失敗的處理
                        status_info['label'].setText(f"❌ 下載失敗")
                        status_info['label'].setStyleSheet("""
                            QLabel {
                                background-color: #ffeaea;
                                border: 1px solid #e74c3c;
                                border-radius: 3px;
                                padding: 4px 6px;
                                margin: 1px;
                                color: #e74c3c;
                            }
                        """)
                        # 隱藏取消按鈕
                        status_info['cancel_btn'].setVisible(False)

                        # 顯示錯誤對話框
                        try:
                            suggestions = self.get_error_suggestions(message)
                            DialogManager.show_download_error(self, message, "", suggestions)
                        except Exception as e:
                            logger.error(f"顯示錯誤對話框失敗: {str(e)}")

                        # 更新統計
                        try:
                            enhanced_setup_manager.update_statistics(False)
                            enhanced_setup_manager.save_settings()
                        except Exception as e:
                            logger.error(f"更新統計失敗: {str(e)}")

                        # 失敗後也要清除狀態
                        QTimer.singleShot(3000, lambda tid=completed_task: self.safe_remove_status_item(tid))

                # 清理完成的任務
                if completed_task in self.current_downloads:
                    del self.current_downloads[completed_task]

            except Exception as e:
                logger.error(f"處理下載完成狀態時發生錯誤: {str(e)}")
                # 即使出錯也要清理任務
                if completed_task and completed_task in self.current_downloads:
                    del self.current_downloads[completed_task]
    
    def hide_status_label(self, task_id):
        """隱藏狀態標籤"""
        if task_id in self.status_labels:
            status_info = self.status_labels[task_id]
            if isinstance(status_info, dict) and 'container' in status_info:
                container = status_info['container']
                self.status_layout.removeWidget(container)
                container.deleteLater()
            del self.status_labels[task_id]

            # 如果沒有狀態標籤了，隱藏整個狀態組
            if not self.status_labels:
                self.status_group.setVisible(False)
    
    def get_error_suggestions(self, error_message):
        """根據錯誤訊息提供建議"""
        suggestions = []
        
        if "年齡驗證" in error_message or "Sign in" in error_message:
            suggestions = [
                "此影片需要年齡驗證，請使用瀏覽器下載",
                "嘗試使用線上下載工具（如 y2mate.com）",
                "尋找相同內容但無年齡限制的影片"
            ]
        elif "網路" in error_message or "network" in error_message.lower():
            suggestions = [
                "檢查網路連接是否正常",
                "嘗試重新啟動程式",
                "稍後再試"
            ]
        else:
            suggestions = [
                "檢查網址是否正確",
                "確認影片是否為公開狀態",
                "嘗試重新輸入網址"
            ]
        
        return suggestions

    def fade_out_status(self, task_id):
        """淡出狀態標籤"""
        if task_id in self.status_labels:
            status_info = self.status_labels[task_id]
            if isinstance(status_info, dict) and 'container' in status_info:
                container = status_info['container']

                # 創建淡出動畫
                from PySide6.QtCore import QPropertyAnimation, QEasingCurve
                from PySide6.QtWidgets import QGraphicsOpacityEffect

                # 添加透明度效果
                opacity_effect = QGraphicsOpacityEffect()
                container.setGraphicsEffect(opacity_effect)

                # 創建動畫
                self.fade_animation = QPropertyAnimation(opacity_effect, b"opacity")
                self.fade_animation.setDuration(1000)  # 1秒淡出
                self.fade_animation.setStartValue(1.0)
                self.fade_animation.setEndValue(0.0)
                self.fade_animation.setEasingCurve(QEasingCurve.OutQuad)

                # 動畫完成後隱藏
                self.fade_animation.finished.connect(lambda: self.hide_status_label(task_id))

                # 開始動畫
                self.fade_animation.start()

    def cancel_download(self, task_id):
        """取消指定的下載"""
        if task_id in self.current_downloads:
            thread = self.current_downloads[task_id]

            # 安全地停止線程
            try:
                if hasattr(thread, 'stop'):
                    thread.stop()  # 如果有stop方法，優先使用
                else:
                    thread.requestInterruption()  # 請求中斷
                    thread.wait(3000)  # 等待3秒
                    if thread.isRunning():
                        thread.terminate()  # 最後才強制終止
                        thread.wait(1000)  # 等待終止完成
            except Exception as e:
                logger.error(f"取消下載時發生錯誤: {str(e)}")

            # 更新狀態
            status_info = self.status_labels.get(task_id)
            if status_info and isinstance(status_info, dict):
                status_info['label'].setText("❌ 已取消")
                status_info['label'].setStyleSheet("""
                    QLabel {
                        background-color: #ffeaea;
                        border: 1px solid #e74c3c;
                        border-radius: 3px;
                        padding: 4px 6px;
                        margin: 1px;
                        color: #e74c3c;
                    }
                """)
                status_info['cancel_btn'].setVisible(False)

            # 清理
            if task_id in self.current_downloads:
                del self.current_downloads[task_id]

            # 3秒後移除狀態項目
            from PySide6.QtCore import QTimer
            QTimer.singleShot(3000, lambda tid=task_id: self.remove_status_item(tid))

            # 3秒後隱藏
            from PySide6.QtCore import QTimer
            QTimer.singleShot(3000, lambda: self.hide_status_label(task_id))

    def clear_all_downloads(self):
        """清除所有下載狀態"""
        # 取消所有進行中的下載
        for task_id in list(self.current_downloads.keys()):
            thread = self.current_downloads[task_id]
            thread.terminate()

        # 清理所有狀態
        self.current_downloads.clear()

        # 清理UI
        for task_id in list(self.status_labels.keys()):
            self.hide_status_label(task_id)

        # 隱藏狀態組
        self.status_group.setVisible(False)

class FinalMainWindow(QMainWindow):
    """最終完整版主視窗"""

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_window_settings()
        self.apply_global_font()
        logger.info("YouTube下載器最終版啟動完成")

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("YouTube下載器 v2.0 - 由 Augment AI 開發")
        self.setMinimumSize(800, 600)

        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # 創建標籤頁
        self.tab_widget = QTabWidget()

        # 下載頁面
        self.download_tab = YouTubeDownloader()
        self.download_tab.download_started.connect(self.on_download_started)

        # 設定頁面
        from ui.unified_settings_tab import UnifiedSettingsTab
        self.settings_tab = UnifiedSettingsTab()
        self.settings_tab.font_size_changed.connect(self.on_font_size_changed)

        # 添加標籤頁
        self.tab_widget.addTab(self.download_tab, "📥 下載")
        self.tab_widget.addTab(self.settings_tab, "⚙️ 設定")

        main_layout.addWidget(self.tab_widget)

        # 狀態欄
        self.statusBar().showMessage("就緒 - 請輸入影片網址開始下載")

    def load_window_settings(self):
        """載入視窗設定"""
        try:
            geometry = enhanced_setup_manager.get_window_geometry()
            self.resize(geometry["width"], geometry["height"])
            self.move(geometry["x"], geometry["y"])

            if enhanced_setup_manager.is_window_maximized():
                self.showMaximized()

            logger.info("視窗設定已載入")
        except Exception as e:
            logger.error(f"載入視窗設定失敗: {str(e)}")

    def save_window_settings(self):
        """保存視窗設定"""
        try:
            enhanced_setup_manager.set_window_maximized(self.isMaximized())

            if not self.isMaximized():
                geometry = self.geometry()
                enhanced_setup_manager.set_window_geometry(
                    geometry.width(),
                    geometry.height(),
                    geometry.x(),
                    geometry.y()
                )

            enhanced_setup_manager.save_settings()
            logger.info("視窗設定已保存")
        except Exception as e:
            logger.error(f"保存視窗設定失敗: {str(e)}")

    def apply_global_font(self):
        """應用全局字體"""
        try:
            font_size = enhanced_setup_manager.get_font_size()
            app = QApplication.instance()
            font = app.font()
            font.setPointSize(font_size)
            app.setFont(font)
            logger.info(f"全局字體大小: {font_size}")
        except Exception as e:
            logger.error(f"設置字體失敗: {str(e)}")

    def on_download_started(self, url, platform_name):
        """處理下載開始"""
        self.statusBar().showMessage(f"正在下載 {platform_name} 影片...")

    def on_font_size_changed(self, size):
        """處理字體變更"""
        self.apply_global_font()

    def closeEvent(self, event):
        """關閉事件"""
        try:
            logger.info("正在關閉程式...")

            # 保存視窗設定
            self.save_window_settings()

            # 保存下載設定
            self.download_tab.save_settings()

            logger.info("程式關閉完成")
            event.accept()

        except Exception as e:
            logger.error(f"關閉程式時出錯: {str(e)}")
            event.accept()

        finally:
            QApplication.instance().quit()

def handle_exception(exc_type, exc_value, exc_traceback):
    """全局異常處理器"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("未捕獲的異常", exc_info=(exc_type, exc_value, exc_traceback))

    # 嘗試顯示錯誤對話框
    try:
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("程式錯誤")
        msg.setText("程式發生未預期的錯誤，但會繼續運行")
        msg.setDetailedText(f"{exc_type.__name__}: {exc_value}")
        msg.exec()
    except:
        pass  # 如果連對話框都無法顯示，就忽略

def main():
    """主函數 - 唯一入口點"""
    # 設定全局異常處理器
    sys.excepthook = handle_exception

    print("=" * 60)
    print("🎬 YouTube下載器 v2.0 - 最終修復版")
    print("=" * 60)
    print("✅ 支援平台：YouTube、Bilibili、TikTok等1000+網站")
    print("✅ 功能完整：下載、設定、彈窗、自動保存")
    print("✅ 簡單易用：輸入網址即可下載")
    print("✅ 穩定可靠：完整的異常處理機制")
    print("=" * 60)

    try:
        app = QApplication(sys.argv)

        # 設置應用程式資訊
        app.setApplicationName("YouTube下載器")
        app.setApplicationVersion("2.0")
        app.setOrganizationName("Augment AI")

        # 創建主視窗
        window = FinalMainWindow()
        window.show()

        print("🚀 程式已啟動，請在GUI中操作")

        # 運行應用程式
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"啟動應用程式時發生錯誤: {str(e)}")
        print(f"❌ 程式啟動失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
