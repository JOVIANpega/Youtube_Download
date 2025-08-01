#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
外部工具管理器 - 方便的新增、修改、刪除功能
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox, QGroupBox, QTextEdit,
    QSplitter, QWidget, QFormLayout
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from enhanced_setup_manager import enhanced_setup_manager
import webbrowser

class ExternalToolsManager(QDialog):
    """外部工具管理器對話框"""
    
    tools_updated = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔗 外部下載工具管理器")
        self.setMinimumSize(800, 600)
        self.init_ui()
        self.load_tools()
    
    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        
        # 標題
        title_label = QLabel("🔗 外部下載工具管理器")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 主要區域 - 分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左側 - 工具列表
        left_widget = self.create_tools_list()
        splitter.addWidget(left_widget)
        
        # 右側 - 編輯區域
        right_widget = self.create_edit_area()
        splitter.addWidget(right_widget)
        
        # 設置分割比例
        splitter.setSizes([300, 500])
        layout.addWidget(splitter)
        
        # 底部按鈕
        button_layout = self.create_bottom_buttons()
        layout.addLayout(button_layout)
    
    def create_tools_list(self):
        """創建工具列表區域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 列表標題
        list_label = QLabel("📋 工具列表")
        list_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(list_label)
        
        # 工具列表
        self.tools_list = QListWidget()
        self.tools_list.itemClicked.connect(self.on_tool_selected)
        layout.addWidget(self.tools_list)
        
        # 列表操作按鈕
        list_button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ 新增")
        self.add_btn.clicked.connect(self.add_new_tool)
        list_button_layout.addWidget(self.add_btn)
        
        self.delete_btn = QPushButton("🗑️ 刪除")
        self.delete_btn.clicked.connect(self.delete_tool)
        self.delete_btn.setEnabled(False)
        list_button_layout.addWidget(self.delete_btn)
        
        layout.addLayout(list_button_layout)
        
        return widget
    
    def create_edit_area(self):
        """創建編輯區域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 編輯標題
        edit_label = QLabel("✏️ 工具編輯")
        edit_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(edit_label)
        
        # 編輯表單
        form_group = QGroupBox("工具資訊")
        form_layout = QFormLayout(form_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：🌐 SaveFrom.net")
        self.name_edit.textChanged.connect(self.on_edit_changed)
        form_layout.addRow("工具名稱:", self.name_edit)
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("例如：https://zh.savefrom.net/#{url}")
        self.url_edit.textChanged.connect(self.on_edit_changed)
        form_layout.addRow("網址模板:", self.url_edit)
        
        # 說明文字
        help_text = QLabel("💡 在網址中使用 {url} 作為影片連結的佔位符")
        help_text.setStyleSheet("color: #666; font-size: 11px; margin: 5px;")
        form_layout.addRow("", help_text)
        
        layout.addWidget(form_group)
        
        # 預覽區域
        preview_group = QGroupBox("🔍 預覽")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_label = QLabel("選擇工具後顯示預覽...")
        self.preview_label.setStyleSheet("color: #666; padding: 10px; border: 1px dashed #ccc;")
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        
        # 測試按鈕
        self.test_btn = QPushButton("🧪 測試工具")
        self.test_btn.clicked.connect(self.test_current_tool)
        self.test_btn.setEnabled(False)
        preview_layout.addWidget(self.test_btn)
        
        layout.addWidget(preview_group)
        
        # 編輯按鈕
        edit_button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("💾 保存")
        self.save_btn.clicked.connect(self.save_current_tool)
        self.save_btn.setEnabled(False)
        edit_button_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("❌ 取消")
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.cancel_btn.setEnabled(False)
        edit_button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(edit_button_layout)
        
        return widget
    
    def create_bottom_buttons(self):
        """創建底部按鈕"""
        layout = QHBoxLayout()
        
        # 重置按鈕
        reset_btn = QPushButton("🔄 重置為預設")
        reset_btn.clicked.connect(self.reset_to_default)
        layout.addWidget(reset_btn)
        
        # 匯入/匯出按鈕
        import_btn = QPushButton("📥 匯入")
        import_btn.clicked.connect(self.import_tools)
        layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 匯出")
        export_btn.clicked.connect(self.export_tools)
        layout.addWidget(export_btn)
        
        layout.addStretch()
        
        # 關閉按鈕
        close_btn = QPushButton("✅ 完成")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        return layout
    
    def load_tools(self):
        """載入工具列表"""
        self.tools_list.clear()
        tools_text = enhanced_setup_manager.get("external_tools", "")
        
        if not tools_text:
            self.reset_to_default()
            return
        
        lines = [line.strip() for line in tools_text.split('\n') if line.strip()]
        for line in lines:
            if '|' in line:
                name, url = line.split('|', 1)
                item = QListWidgetItem(name.strip())
                item.setData(Qt.UserRole, url.strip())
                self.tools_list.addItem(item)
    
    def on_tool_selected(self, item):
        """工具選中處理"""
        name = item.text()
        url = item.data(Qt.UserRole)
        
        self.name_edit.setText(name)
        self.url_edit.setText(url)
        
        # 更新預覽
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        preview_url = url.replace('{url}', test_url)
        self.preview_label.setText(f"工具名稱: {name}\n網址模板: {url}\n\n測試預覽:\n{preview_url}")
        
        # 啟用按鈕
        self.delete_btn.setEnabled(True)
        self.test_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
    
    def on_edit_changed(self):
        """編輯內容變更"""
        name = self.name_edit.text().strip()
        url = self.url_edit.text().strip()
        
        if name and url:
            test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
            preview_url = url.replace('{url}', test_url)
            self.preview_label.setText(f"工具名稱: {name}\n網址模板: {url}\n\n測試預覽:\n{preview_url}")
            self.test_btn.setEnabled(True)
        else:
            self.preview_label.setText("請填寫完整的工具資訊...")
            self.test_btn.setEnabled(False)
    
    def add_new_tool(self):
        """新增工具"""
        self.name_edit.clear()
        self.url_edit.clear()
        self.preview_label.setText("請填寫新工具的資訊...")
        
        # 清除選擇
        self.tools_list.clearSelection()
        self.delete_btn.setEnabled(False)
        self.save_btn.setEnabled(True)
        self.cancel_btn.setEnabled(True)
        self.test_btn.setEnabled(False)
    
    def delete_tool(self):
        """刪除工具"""
        current_item = self.tools_list.currentItem()
        if not current_item:
            return
        
        reply = QMessageBox.question(
            self, "確認刪除", 
            f"確定要刪除工具 '{current_item.text()}' 嗎？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            row = self.tools_list.row(current_item)
            self.tools_list.takeItem(row)
            self.save_tools()
            self.clear_edit_area()
    
    def save_current_tool(self):
        """保存當前工具"""
        name = self.name_edit.text().strip()
        url = self.url_edit.text().strip()
        
        if not name or not url:
            QMessageBox.warning(self, "錯誤", "請填寫完整的工具資訊")
            return
        
        if '{url}' not in url:
            reply = QMessageBox.question(
                self, "確認", 
                "網址模板中沒有 {url} 佔位符，確定要保存嗎？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # 檢查是否是編輯現有工具
        current_item = self.tools_list.currentItem()
        if current_item:
            # 編輯現有工具
            current_item.setText(name)
            current_item.setData(Qt.UserRole, url)
        else:
            # 新增工具
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, url)
            self.tools_list.addItem(item)
        
        self.save_tools()
        self.clear_edit_area()
    
    def cancel_edit(self):
        """取消編輯"""
        self.clear_edit_area()
    
    def clear_edit_area(self):
        """清空編輯區域"""
        self.name_edit.clear()
        self.url_edit.clear()
        self.preview_label.setText("選擇工具後顯示預覽...")
        self.tools_list.clearSelection()
        
        self.delete_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.test_btn.setEnabled(False)
    
    def test_current_tool(self):
        """測試當前工具"""
        url = self.url_edit.text().strip()
        if not url:
            return
        
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        final_url = url.replace('{url}', test_url)
        
        try:
            webbrowser.open(final_url)
        except Exception as e:
            QMessageBox.warning(self, "錯誤", f"無法打開網址：{str(e)}")
    
    def save_tools(self):
        """保存工具列表到設定"""
        tools = []
        for i in range(self.tools_list.count()):
            item = self.tools_list.item(i)
            name = item.text()
            url = item.data(Qt.UserRole)
            tools.append(f"{name}|{url}")
        
        tools_text = "\n".join(tools)
        enhanced_setup_manager.set("external_tools", tools_text)
        enhanced_setup_manager.save_settings()
        self.tools_updated.emit()
    
    def reset_to_default(self):
        """重置為預設工具"""
        reply = QMessageBox.question(
            self, "確認重置", 
            "確定要重置為預設工具嗎？這將覆蓋所有自定義工具。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
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
            enhanced_setup_manager.set("external_tools", tools_text)
            enhanced_setup_manager.save_settings()
            self.load_tools()
            self.tools_updated.emit()
    
    def import_tools(self):
        """匯入工具（從剪貼簿或檔案）"""
        QMessageBox.information(self, "功能開發中", "匯入功能將在下個版本中提供")
    
    def export_tools(self):
        """匯出工具（到剪貼簿或檔案）"""
        QMessageBox.information(self, "功能開發中", "匯出功能將在下個版本中提供")
