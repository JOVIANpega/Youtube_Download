#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查依賴項
"""

import sys

def check_python_version():
    """檢查 Python 版本"""
    version = sys.version_info
    print(f"Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 版本過低，需要 Python 3.7+")
        return False
    else:
        print("✅ Python 版本符合要求")
        return True

def check_tkinter():
    """檢查 Tkinter"""
    try:
        import tkinter as tk
        from tkinter import ttk
        print("✅ Tkinter 可用")
        return True
    except ImportError:
        print("❌ Tkinter 不可用")
        print("   在 Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   在 CentOS/RHEL: sudo yum install tkinter")
        return False

def check_optional_dependencies():
    """檢查可選依賴"""
    deps = {
        'yt-dlp': 'pip install yt-dlp',
        'requests': 'pip install requests',
    }
    
    missing = []
    
    for dep, install_cmd in deps.items():
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep} 已安裝")
        except ImportError:
            print(f"⚠️  {dep} 未安裝 - {install_cmd}")
            missing.append(dep)
    
    return missing

def main():
    """主函數"""
    print("YouTube 下載器 - 依賴檢查")
    print("=" * 40)
    
    # 檢查 Python 版本
    if not check_python_version():
        return False
    
    print()
    
    # 檢查 Tkinter
    if not check_tkinter():
        return False
    
    print()
    
    # 檢查可選依賴
    missing = check_optional_dependencies()
    
    print()
    print("=" * 40)
    
    if missing:
        print("⚠️  部分功能可能不可用")
        print("缺少的依賴:")
        for dep in missing:
            print(f"  - {dep}")
        print("\n可以運行簡化版本: python simple_main.py")
        print("安裝完整依賴後運行: python main.py")
    else:
        print("✅ 所有依賴都已安裝")
        print("可以運行完整版本: python main.py")
    
    return len(missing) == 0

if __name__ == "__main__":
    main()