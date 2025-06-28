#!/usr/bin/env python3
"""
快速測試腳本
Quick Test Script
クイックテストスクリプト
퀵 테스트 스크립트
"""

import sys
import os
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

class QuickTestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("快速測試")
        self.setMinimumSize(400, 300)
        
        # 創建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 創建主佈局
        layout = QVBoxLayout(central_widget)
        
        # 標題
        title_label = QLabel("按鈕測試")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title_label)
        
        # 測試按鈕 1
        self.test_button1 = QPushButton("測試按鈕 1")
        self.test_button1.clicked.connect(self.test_button1_click)
        self.test_button1.setStyleSheet("font-size: 14px; padding: 10px; background-color: #2196F3; color: white;")
        layout.addWidget(self.test_button1)
        
        # 測試按鈕 2
        self.test_button2 = QPushButton("測試按鈕 2")
        self.test_button2.clicked.connect(self.test_button2_click)
        self.test_button2.setStyleSheet("font-size: 14px; padding: 10px; background-color: #4CAF50; color: white;")
        layout.addWidget(self.test_button2)
        
        # 測試按鈕 3
        self.test_button3 = QPushButton("測試按鈕 3")
        self.test_button3.clicked.connect(self.test_button3_click)
        self.test_button3.setStyleSheet("font-size: 14px; padding: 10px; background-color: #FF9800; color: white;")
        layout.addWidget(self.test_button3)
        
        # 狀態標籤
        self.status_label = QLabel("等待按鈕點擊...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; margin: 10px; color: #666;")
        layout.addWidget(self.status_label)
    
    def test_button1_click(self):
        """測試按鈕 1 點擊事件"""
        self.status_label.setText("✓ 測試按鈕 1 被點擊了！")
        self.status_label.setStyleSheet("font-size: 12px; margin: 10px; color: #2196F3; font-weight: bold;")
        print("測試按鈕 1 被點擊")
    
    def test_button2_click(self):
        """測試按鈕 2 點擊事件"""
        self.status_label.setText("✓ 測試按鈕 2 被點擊了！")
        self.status_label.setStyleSheet("font-size: 12px; margin: 10px; color: #4CAF50; font-weight: bold;")
        print("測試按鈕 2 被點擊")
    
    def test_button3_click(self):
        """測試按鈕 3 點擊事件"""
        self.status_label.setText("✓ 測試按鈕 3 被點擊了！")
        self.status_label.setStyleSheet("font-size: 12px; margin: 10px; color: #FF9800; font-weight: bold;")
        print("測試按鈕 3 被點擊")

def main():
    app = QApplication(sys.argv)
    window = QuickTestWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 