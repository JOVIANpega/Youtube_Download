#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
統一設定頁面
將所有設定合併到一個滾動頁面中
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QPushButton, QGroupBox, QCheckBox, QSpinBox, QFileDialog, QMessageBox,
    QScrollArea, QFormLayout, QSlider, QTextEdit
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from enhanced_setup_manager import enhanced_setup_manager
from ui.dialog_manager import DialogManager
from logger import logger

class UnifiedSettingsTab(QWidget):
    """統一設定頁面"""
    
    settings_changed = Signal()
    font_size_changed = Signal(int)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.load_settings()
    
    def init_ui(self):
        """初始化UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 創建滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 滾動內容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        
        # 創建各個設定組
        self.create_basic_settings(scroll_layout)
        self.create_ui_settings(scroll_layout)
        self.create_network_settings(scroll_layout)
        # 移除平台設定 - 支援所有平台
        # self.create_platform_settings(scroll_layout)
        self.create_external_tools_settings(scroll_layout)
        self.create_advanced_settings(scroll_layout)
        self.create_statistics_display(scroll_layout)
        
        # 添加彈性空間
        scroll_layout.addStretch()
        
        # 設置滾動區域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 底部按鈕
        self.create_bottom_buttons(main_layout)
    
    def create_basic_settings(self, layout):
        """創建基本設定"""
        group = QGroupBox("📁 基本設定")
        group_layout = QFormLayout(group)
        
        # 下載路徑
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setMaxLength(150)  # 限制150字元
        self.path_edit.setMinimumWidth(250)  # 縮短寬度
        self.path_edit.setMaximumWidth(350)  # 限制最大寬度
        self.path_edit.textChanged.connect(self.on_path_changed)
        
        browse_button = QPushButton("瀏覽")
        browse_button.clicked.connect(self.browse_download_path)
        
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(browse_button)
        group_layout.addRow("下載路徑:", path_layout)
        
        # 檔名前綴
        prefix_layout = QHBoxLayout()
        self.prefix_edit = QLineEdit()
        self.prefix_edit.setMaxLength(15)  # 限制15字元
        self.prefix_edit.setMinimumWidth(150)  # 縮短寬度
        self.prefix_edit.setMaximumWidth(200)  # 限制最大寬度
        self.prefix_edit.textChanged.connect(self.on_prefix_changed)
        
        self.prefix_length_label = QLabel("0/15")
        self.prefix_length_label.setStyleSheet("color: #666; font-size: 10px;")
        
        prefix_layout.addWidget(self.prefix_edit)
        prefix_layout.addWidget(self.prefix_length_label)
        group_layout.addRow("檔名前綴:", prefix_layout)
        
        # 格式選項
        self.format_combo = QComboBox()
        self.format_combo.addItems(["最高品質", "高品質", "中等品質", "僅音頻"])
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        group_layout.addRow("下載格式:", self.format_combo)
        
        # 解析度
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["1080P", "720P", "480P", "360P", "自動"])
        self.resolution_combo.currentTextChanged.connect(self.on_resolution_changed)
        group_layout.addRow("影片解析度:", self.resolution_combo)
        
        # 自動合併
        self.auto_merge_cb = QCheckBox("自動合併音視頻")
        self.auto_merge_cb.stateChanged.connect(self.on_auto_merge_changed)
        group_layout.addRow("", self.auto_merge_cb)
        
        layout.addWidget(group)
    
    def create_ui_settings(self, layout):
        """創建UI設定"""
        group = QGroupBox("🎨 界面設定")
        group_layout = QFormLayout(group)
        
        # 字體大小
        font_layout = QHBoxLayout()
        
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setRange(10, 15)  # 限制範圍10-15
        self.font_slider.setValue(11)
        self.font_slider.valueChanged.connect(self.on_font_size_changed)
        
        self.font_size_label = QLabel("11")
        self.font_size_label.setMinimumWidth(30)
        
        font_minus_btn = QPushButton("-")
        font_minus_btn.setMaximumWidth(30)
        font_minus_btn.clicked.connect(lambda: self.adjust_font_size(-1))
        
        font_plus_btn = QPushButton("+")
        font_plus_btn.setMaximumWidth(30)
        font_plus_btn.clicked.connect(lambda: self.adjust_font_size(1))
        
        font_layout.addWidget(font_minus_btn)
        font_layout.addWidget(self.font_slider)
        font_layout.addWidget(font_plus_btn)
        font_layout.addWidget(self.font_size_label)
        
        group_layout.addRow("字體大小:", font_layout)
        
        # UI選項
        self.show_complete_dialog_cb = QCheckBox("下載完成時顯示對話框")
        self.show_complete_dialog_cb.stateChanged.connect(self.on_ui_option_changed)
        group_layout.addRow("", self.show_complete_dialog_cb)
        
        self.auto_clear_completed_cb = QCheckBox("自動清除已完成的下載")
        self.auto_clear_completed_cb.stateChanged.connect(self.on_ui_option_changed)
        group_layout.addRow("", self.auto_clear_completed_cb)
        
        layout.addWidget(group)
    
    def create_network_settings(self, layout):
        """創建網路設定"""
        group = QGroupBox("🌐 網路設定")
        group_layout = QFormLayout(group)
        
        # 超時時間
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setSuffix(" 秒")
        self.timeout_spin.valueChanged.connect(self.on_network_changed)
        group_layout.addRow("連接超時:", self.timeout_spin)
        
        # 重試次數
        self.retry_spin = QSpinBox()
        self.retry_spin.setRange(1, 10)
        self.retry_spin.valueChanged.connect(self.on_network_changed)
        group_layout.addRow("重試次數:", self.retry_spin)
        
        # 最大同時下載數
        self.max_downloads_spin = QSpinBox()
        self.max_downloads_spin.setRange(1, 10)
        self.max_downloads_spin.valueChanged.connect(self.on_network_changed)
        group_layout.addRow("最大同時下載:", self.max_downloads_spin)
        
        layout.addWidget(group)

    def create_external_tools_settings(self, layout):
        """創建外部工具設定"""
        group = QGroupBox("🔗 外部下載工具")
        group_layout = QVBoxLayout(group)

        # 說明文字
        info_label = QLabel("管理外部下載工具網址，每行一個工具，格式：名稱|網址")
        info_label.setStyleSheet("color: #666; font-size: 10px; margin-bottom: 5px;")
        group_layout.addWidget(info_label)

        # 外部工具列表編輯器
        self.external_tools_edit = QTextEdit()
        self.external_tools_edit.setMaximumHeight(150)
        self.external_tools_edit.setPlaceholderText(
            "🌐 SaveFrom.net|https://zh.savefrom.net/#{url}\n"
            "🎬 Y2Mate|https://www.y2mate.com/zh-cn/youtube/{url}\n"
            "📱 SnapSave|https://snapsave.app/zh?url={url}"
        )
        self.external_tools_edit.textChanged.connect(self.on_external_tools_changed)
        group_layout.addWidget(self.external_tools_edit)

        # 按鈕區域
        button_layout = QHBoxLayout()

        # 重置為預設按鈕
        reset_btn = QPushButton("🔄 重置預設")
        reset_btn.setMaximumWidth(100)
        reset_btn.clicked.connect(self.reset_external_tools)
        button_layout.addWidget(reset_btn)

        # 測試按鈕
        test_btn = QPushButton("🧪 測試工具")
        test_btn.setMaximumWidth(100)
        test_btn.clicked.connect(self.test_external_tools)
        button_layout.addWidget(test_btn)

        button_layout.addStretch()
        group_layout.addLayout(button_layout)

        layout.addWidget(group)

    def create_platform_settings(self, layout):
        """創建平台設定"""
        group = QGroupBox("🎬 平台設定")
        group_layout = QVBoxLayout(group)
        
        # 平台開關
        platforms_layout = QFormLayout()
        
        self.platform_checkboxes = {}
        platforms = [
            ("YouTube", "youtube_enabled"),
            ("Bilibili", "bilibili_enabled"),
            ("TikTok", "tiktok_enabled"),
            ("抖音", "douyin_enabled"),
            ("Instagram", "instagram_enabled"),
            ("Facebook", "facebook_enabled")
        ]
        
        for platform_name, setting_key in platforms:
            checkbox = QCheckBox(f"啟用 {platform_name}")
            checkbox.stateChanged.connect(self.on_platform_changed)
            platforms_layout.addRow("", checkbox)
            self.platform_checkboxes[setting_key] = checkbox
        
        group_layout.addLayout(platforms_layout)
        layout.addWidget(group)
    
    def create_advanced_settings(self, layout):
        """創建進階設定"""
        group = QGroupBox("⚙️ 進階設定")
        group_layout = QFormLayout(group)
        
        # 進階選項
        self.keep_temp_cb = QCheckBox("保留臨時檔案")
        self.keep_temp_cb.stateChanged.connect(self.on_advanced_changed)
        group_layout.addRow("", self.keep_temp_cb)
        
        self.auto_open_folder_cb = QCheckBox("下載完成後自動打開目錄")
        self.auto_open_folder_cb.stateChanged.connect(self.on_advanced_changed)
        group_layout.addRow("", self.auto_open_folder_cb)
        
        self.auto_play_video_cb = QCheckBox("下載完成後自動播放影片")
        self.auto_play_video_cb.stateChanged.connect(self.on_advanced_changed)
        group_layout.addRow("", self.auto_play_video_cb)
        
        # 移除字幕下載選項
        # self.download_subtitles_cb = QCheckBox("同時下載字幕")
        # self.download_subtitles_cb.stateChanged.connect(self.on_advanced_changed)
        # group_layout.addRow("", self.download_subtitles_cb)
        
        self.prefer_mp4_cb = QCheckBox("優先選擇MP4格式")
        self.prefer_mp4_cb.stateChanged.connect(self.on_advanced_changed)
        group_layout.addRow("", self.prefer_mp4_cb)

        # SSL/網路選項
        ssl_layout = QHBoxLayout()

        self.update_ssl_btn = QPushButton("🔄 更新SSL憑證")
        self.update_ssl_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        self.update_ssl_btn.clicked.connect(self.update_ssl_certificates)

        self.update_ytdl_btn = QPushButton("📥 更新yt-dlp")
        self.update_ytdl_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 11px;
            }
            QPushButton:hover { background-color: #8e44ad; }
        """)
        self.update_ytdl_btn.clicked.connect(self.update_ytdlp)

        ssl_layout.addWidget(self.update_ssl_btn)
        ssl_layout.addWidget(self.update_ytdl_btn)
        ssl_layout.addStretch()

        group_layout.addRow("網路更新:", ssl_layout)
        
        layout.addWidget(group)
    
    def create_statistics_display(self, layout):
        """創建統計資訊顯示"""
        group = QGroupBox("📊 統計資訊")
        group_layout = QFormLayout(group)
        
        self.stats_labels = {}
        stats_items = [
            ("total_downloads", "總下載次數:"),
            ("successful_downloads", "成功下載:"),
            ("failed_downloads", "失敗下載:"),
            ("total_size_downloaded", "總下載大小:")
        ]
        
        for key, label_text in stats_items:
            label = QLabel("0")
            label.setStyleSheet("color: #2c3e50; font-weight: bold;")
            group_layout.addRow(label_text, label)
            self.stats_labels[key] = label
        
        layout.addWidget(group)
    
    def create_bottom_buttons(self, layout):
        """創建底部按鈕"""
        button_layout = QHBoxLayout()
        
        # 匯入/匯出按鈕
        import_button = QPushButton("📥 匯入設定")
        import_button.clicked.connect(self.import_settings)
        
        export_button = QPushButton("📤 匯出設定")
        export_button.clicked.connect(self.export_settings)
        
        # 主要按鈕
        reset_button = QPushButton("🔄 重置為預設值")
        reset_button.clicked.connect(self.reset_to_defaults)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        
        save_button = QPushButton("💾 儲存設定")
        save_button.clicked.connect(self.save_settings)
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        
        apply_button = QPushButton("✅ 立即應用")
        apply_button.clicked.connect(self.apply_settings)
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        
        button_layout.addWidget(import_button)
        button_layout.addWidget(export_button)
        button_layout.addStretch()
        button_layout.addWidget(reset_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(apply_button)
        
        layout.addLayout(button_layout)

    def load_settings(self):
        """載入設定"""
        # 基本設定
        self.path_edit.setText(enhanced_setup_manager.get("download_path", "M:/TEMP"))
        self.prefix_edit.setText(enhanced_setup_manager.get("filename_prefix", ""))
        self.format_combo.setCurrentText(enhanced_setup_manager.get("format_option", "最高品質"))
        self.resolution_combo.setCurrentText(enhanced_setup_manager.get("resolution", "720P"))
        self.auto_merge_cb.setChecked(enhanced_setup_manager.get("auto_merge", True))

        # UI設定
        font_size = enhanced_setup_manager.get_font_size()
        self.font_slider.setValue(font_size)
        self.font_size_label.setText(str(font_size))

        self.show_complete_dialog_cb.setChecked(
            enhanced_setup_manager.get("advanced_settings.show_download_complete_dialog", True)
        )
        self.auto_clear_completed_cb.setChecked(
            enhanced_setup_manager.get("advanced_settings.auto_clear_completed", True)
        )

        # 網路設定
        self.timeout_spin.setValue(enhanced_setup_manager.get("timeout", 30))
        self.retry_spin.setValue(enhanced_setup_manager.get("retry_count", 3))
        self.max_downloads_spin.setValue(enhanced_setup_manager.get("max_concurrent_downloads", 5))

        # 平台設定 - 已移除
        # for setting_key, checkbox in self.platform_checkboxes.items():
        #     enabled = enhanced_setup_manager.get(f"platform_settings.{setting_key}", True)
        #     checkbox.setChecked(enabled)

        # 進階設定
        self.keep_temp_cb.setChecked(
            enhanced_setup_manager.get("advanced_settings.keep_temp_files", False)
        )
        self.auto_open_folder_cb.setChecked(
            enhanced_setup_manager.get("advanced_settings.auto_open_folder", True)
        )
        self.auto_play_video_cb.setChecked(
            enhanced_setup_manager.get("advanced_settings.auto_play_video", False)
        )
        # 字幕下載設定 - 已移除
        # self.download_subtitles_cb.setChecked(
        #     enhanced_setup_manager.get("advanced_settings.download_subtitles", False)
        # )
        self.prefer_mp4_cb.setChecked(
            enhanced_setup_manager.get("advanced_settings.prefer_mp4", True)
        )

        # 外部工具設定
        external_tools = enhanced_setup_manager.get("external_tools", "")
        if not external_tools:
            # 如果沒有設定，使用預設值
            self.reset_external_tools()
        else:
            self.external_tools_edit.setPlainText(external_tools)

        # 更新統計資訊
        self.update_statistics_display()

        # 更新前綴計數
        self.on_prefix_changed()

    def update_statistics_display(self):
        """更新統計資訊顯示"""
        stats = enhanced_setup_manager.get("statistics", {})

        self.stats_labels["total_downloads"].setText(str(stats.get("total_downloads", 0)))
        self.stats_labels["successful_downloads"].setText(str(stats.get("successful_downloads", 0)))
        self.stats_labels["failed_downloads"].setText(str(stats.get("failed_downloads", 0)))

        # 格式化下載大小
        total_size = stats.get("total_size_downloaded", 0)
        if total_size > 1024 * 1024 * 1024:  # GB
            size_text = f"{total_size / (1024 * 1024 * 1024):.1f} GB"
        elif total_size > 1024 * 1024:  # MB
            size_text = f"{total_size / (1024 * 1024):.1f} MB"
        else:  # KB
            size_text = f"{total_size / 1024:.1f} KB"

        self.stats_labels["total_size_downloaded"].setText(size_text)

    # 事件處理方法
    def on_path_changed(self):
        """路徑變更處理"""
        path = self.path_edit.text()
        enhanced_setup_manager.set("download_path", path)
        enhanced_setup_manager.add_recent_path(path)
        self.auto_save()

    def on_prefix_changed(self):
        """前綴變更處理"""
        text = self.prefix_edit.text()
        length = len(text)
        self.prefix_length_label.setText(f"{length}/15")

        if length > 15:
            self.prefix_length_label.setStyleSheet("color: red; font-size: 10px;")
        else:
            self.prefix_length_label.setStyleSheet("color: #666; font-size: 10px;")

        enhanced_setup_manager.set("filename_prefix", text)
        self.auto_save()

    def on_format_changed(self):
        """格式變更處理"""
        enhanced_setup_manager.set("format_option", self.format_combo.currentText())
        self.auto_save()

    def on_resolution_changed(self):
        """解析度變更處理"""
        enhanced_setup_manager.set("resolution", self.resolution_combo.currentText())
        self.auto_save()

    def on_auto_merge_changed(self):
        """自動合併變更處理"""
        enhanced_setup_manager.set("auto_merge", self.auto_merge_cb.isChecked())
        self.auto_save()

    def on_font_size_changed(self, size):
        """字體大小變更處理"""
        self.font_size_label.setText(str(size))
        enhanced_setup_manager.set_font_size(size)
        self.font_size_changed.emit(size)
        self.auto_save()

    def adjust_font_size(self, delta):
        """調整字體大小"""
        current_size = self.font_slider.value()
        new_size = max(10, min(15, current_size + delta))
        self.font_slider.setValue(new_size)

    def on_ui_option_changed(self):
        """UI選項變更處理"""
        enhanced_setup_manager.set(
            "advanced_settings.show_download_complete_dialog",
            self.show_complete_dialog_cb.isChecked()
        )
        enhanced_setup_manager.set(
            "advanced_settings.auto_clear_completed",
            self.auto_clear_completed_cb.isChecked()
        )
        self.auto_save()

    def on_network_changed(self):
        """網路設定變更處理"""
        enhanced_setup_manager.set("timeout", self.timeout_spin.value())
        enhanced_setup_manager.set("retry_count", self.retry_spin.value())
        enhanced_setup_manager.set("max_concurrent_downloads", self.max_downloads_spin.value())
        self.auto_save()

    def on_platform_changed(self):
        """平台設定變更處理"""
        for setting_key, checkbox in self.platform_checkboxes.items():
            enhanced_setup_manager.set(f"platform_settings.{setting_key}", checkbox.isChecked())
        self.auto_save()

    def on_advanced_changed(self):
        """進階設定變更處理"""
        enhanced_setup_manager.set(
            "advanced_settings.keep_temp_files",
            self.keep_temp_cb.isChecked()
        )
        enhanced_setup_manager.set(
            "advanced_settings.auto_open_folder",
            self.auto_open_folder_cb.isChecked()
        )
        enhanced_setup_manager.set(
            "advanced_settings.auto_play_video",
            self.auto_play_video_cb.isChecked()
        )
        # 字幕下載設定 - 已移除
        # enhanced_setup_manager.set(
        #     "advanced_settings.download_subtitles",
        #     self.download_subtitles_cb.isChecked()
        # )
        enhanced_setup_manager.set(
            "advanced_settings.prefer_mp4",
            self.prefer_mp4_cb.isChecked()
        )
        self.auto_save()

    def browse_download_path(self):
        """瀏覽下載路徑"""
        current_path = self.path_edit.text() or "M:/TEMP"
        path = QFileDialog.getExistingDirectory(self, "選擇下載路徑", current_path)
        if path:
            self.path_edit.setText(path)

    def auto_save(self):
        """自動保存設定"""
        enhanced_setup_manager.save_settings()

    def save_settings(self):
        """手動保存設定"""
        if enhanced_setup_manager.save_settings():
            DialogManager.show_settings_saved(self)
        self.settings_changed.emit()

    def apply_settings(self):
        """立即應用設定"""
        self.save_settings()
        logger.info("設定已立即應用")

    def reset_to_defaults(self):
        """重置為預設值"""
        if DialogManager.confirm_reset_settings(self):
            enhanced_setup_manager.reset_to_defaults()
            enhanced_setup_manager.save_settings()
            self.load_settings()
            self.settings_changed.emit()
            QMessageBox.information(self, "重置完成", "所有設定已重置為預設值！")

    def import_settings(self):
        """匯入設定"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "匯入設定", "", "JSON files (*.json)"
        )
        if file_path:
            if enhanced_setup_manager.import_settings(file_path):
                self.load_settings()
                self.settings_changed.emit()
                QMessageBox.information(self, "匯入成功", f"設定已從 {file_path} 匯入！")
            else:
                QMessageBox.warning(self, "匯入失敗", "無法匯入設定文件，請檢查文件格式。")

    def export_settings(self):
        """匯出設定"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "匯出設定", "youtube_downloader_settings.json", "JSON files (*.json)"
        )
        if file_path:
            if enhanced_setup_manager.export_settings(file_path):
                QMessageBox.information(self, "匯出成功", f"設定已匯出到 {file_path}！")
            else:
                QMessageBox.warning(self, "匯出失敗", "無法匯出設定文件。")

    def update_ssl_certificates(self):
        """更新SSL憑證"""
        reply = QMessageBox.question(
            self, "更新SSL憑證",
            "🔄 確定要更新SSL憑證嗎？\n\n這將：\n• 清除舊的SSL快取\n• 重新下載最新憑證\n• 解決部分網路連接問題\n\n過程可能需要幾秒鐘。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            try:
                import ssl
                import certifi
                import subprocess
                import sys

                # 更新certifi
                result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "certifi"],
                                      capture_output=True, text=True)

                if result.returncode == 0:
                    QMessageBox.information(self, "更新成功", "✅ SSL憑證已成功更新！\n\n建議重新啟動程式以確保變更生效。")
                else:
                    QMessageBox.warning(self, "更新失敗", f"❌ SSL憑證更新失敗：\n{result.stderr}")

            except Exception as e:
                QMessageBox.warning(self, "更新失敗", f"❌ SSL憑證更新失敗：\n{str(e)}")

    def update_ytdlp(self):
        """更新yt-dlp"""
        reply = QMessageBox.question(
            self, "更新yt-dlp",
            "📥 確定要更新yt-dlp嗎？\n\n這將：\n• 更新到最新版本\n• 支援更多網站\n• 修復已知問題\n• 提升下載成功率\n\n過程可能需要幾分鐘。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )

        if reply == QMessageBox.Yes:
            try:
                import subprocess
                import sys

                # 更新yt-dlp
                result = subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
                                      capture_output=True, text=True)

                if result.returncode == 0:
                    QMessageBox.information(self, "更新成功", "✅ yt-dlp已成功更新！\n\n新版本將在下次下載時生效。")
                else:
                    QMessageBox.warning(self, "更新失敗", f"❌ yt-dlp更新失敗：\n{result.stderr}")

            except Exception as e:
                QMessageBox.warning(self, "更新失敗", f"❌ yt-dlp更新失敗：\n{str(e)}")

    def on_external_tools_changed(self):
        """外部工具變更處理"""
        tools_text = self.external_tools_edit.toPlainText()
        enhanced_setup_manager.set("external_tools", tools_text)
        self.auto_save()

    def reset_external_tools(self):
        """重置外部工具為預設值"""
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
        self.external_tools_edit.setPlainText("\n".join(default_tools))

    def test_external_tools(self):
        """測試外部工具"""
        tools_text = self.external_tools_edit.toPlainText()
        if not tools_text.strip():
            QMessageBox.warning(self, "提示", "請先添加外部工具")
            return

        lines = [line.strip() for line in tools_text.split('\n') if line.strip()]
        valid_count = 0

        for line in lines:
            if '|' in line:
                valid_count += 1

        QMessageBox.information(
            self,
            "測試結果",
            f"共找到 {len(lines)} 行\n有效工具: {valid_count} 個\n\n"
            f"格式要求：名稱|網址\n"
            f"網址中使用 {{url}} 作為影片連結佔位符"
        )
