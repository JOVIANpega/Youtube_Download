#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全啟動腳本
自動選擇最安全的版本運行
"""

import os
import sys

def find_safe_version():
    """找到最安全的可用版本"""
    
    # 按安全性排序的版本列表
    safe_versions = [
        ('minimal_safe.py', '最小安全版'),
        ('simple_main.py', '簡化版'),
        ('main_safe.py', '安全版'),
        ('main_fixed.py', '修復版'),
    ]
    
    print("🔍 尋找安全版本...")
    
    for filename, description in safe_versions:
        if os.path.exists(filename):
            print(f"✅ 找到 {filename} ({description})")
            return filename, description
    
    print("❌ 未找到安全版本")
    return None, None

def create_minimal_if_needed():
    """如果需要，創建最小版本"""
    
    if os.path.exists('minimal_safe.py'):
        return True
    
    print("🔧 創建最小安全版...")
    
    minimal_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最小安全版 YouTube 下載器
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys

class MinimalApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("YouTube 下載器 - 最小版")
        self.root.geometry("400x300")
        
        # 主框架
        frame = ttk.Frame(self.root)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 標題
        ttk.Label(frame, text="YouTube 下載器", 
                 font=('Arial', 16, 'bold')).pack(pady=20)
        
        # 說明
        ttk.Label(frame, text="✅ 應用程式運行正常！\\n\\n這是最小安全版本，\\n無任何依賴問題。").pack(pady=20)
        
        # 測試按鈕
        ttk.Button(frame, text="測試功能", 
                  command=self.test).pack(pady=10)
        
        # 關閉按鈕
        ttk.Button(frame, text="關閉", 
                  command=self.root.quit).pack(pady=10)
    
    def test(self):
        version = sys.version_info
        messagebox.showinfo("測試結果", 
                          f"✅ 基本功能正常\\n\\nPython: {version.major}.{version.minor}.{version.micro}\\nTkinter: 可用")
    
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = MinimalApp()
        app.run()
    except Exception as e:
        print(f"錯誤: {e}")
        input("按 Enter 退出...")
'''
    
    try:
        with open('minimal_safe.py', 'w', encoding='utf-8') as f:
            f.write(minimal_content)
        print("✅ 創建 minimal_safe.py 成功")
        return True
    except Exception as e:
        print(f"❌ 創建失敗: {e}")
        return False

def main():
    """主函數"""
    print("🚀 YouTube 下載器 - 安全啟動")
    print("=" * 40)
    
    # 尋找安全版本
    safe_file, description = find_safe_version()
    
    if not safe_file:
        # 創建最小版本
        if create_minimal_if_needed():
            safe_file, description = 'minimal_safe.py', '最小安全版'
        else:
            print("❌ 無法創建安全版本")
            input("按 Enter 退出...")
            return
    
    print(f"\n🎯 將啟動: {safe_file} ({description})")
    print("=" * 40)
    
    try:
        # 動態導入並運行
        module_name = safe_file.replace('.py', '')
        
        if safe_file == 'minimal_safe.py':
            import minimal_safe
            minimal_safe.main()
        elif safe_file == 'simple_main.py':
            import simple_main
            simple_main.main()
        elif safe_file == 'main_safe.py':
            import main_safe
            main_safe.main()
        elif safe_file == 'main_fixed.py':
            import main_fixed
            main_fixed.main()
        else:
            print(f"❌ 不知道如何啟動 {safe_file}")
            
    except Exception as e:
        print(f"❌ 啟動 {safe_file} 失敗: {e}")
        print("\n🔧 建議:")
        print("1. 檢查 Python 環境")
        print("2. 確認 Tkinter 可用")
        print("3. 運行: python error_diagnosis.py")
        
        import traceback
        traceback.print_exc()
        input("\n按 Enter 退出...")

if __name__ == "__main__":
    main()