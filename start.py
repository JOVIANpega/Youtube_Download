#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 下載器啟動腳本
自動檢查環境並選擇最佳啟動方式
"""

import sys
import os

# 添加當前目錄到路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_environment():
    """檢查運行環境"""
    print("🔍 檢查運行環境...")
    
    # 檢查 Python 版本
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print(f"❌ Python 版本過低: {version.major}.{version.minor}")
        print("   需要 Python 3.7 或更高版本")
        return False
    
    print(f"✅ Python 版本: {version.major}.{version.minor}.{version.micro}")
    
    # 檢查 Tkinter
    try:
        import tkinter
        print("✅ Tkinter 可用")
    except ImportError:
        print("❌ Tkinter 不可用")
        print("   請安裝 python3-tk 套件")
        return False
    
    return True

def check_dependencies():
    """檢查可選依賴"""
    print("\n📦 檢查依賴套件...")
    
    deps_status = {}
    
    # 檢查 yt-dlp
    try:
        import yt_dlp
        deps_status['yt-dlp'] = True
        print("✅ yt-dlp 已安裝")
    except ImportError:
        deps_status['yt-dlp'] = False
        print("⚠️  yt-dlp 未安裝 (下載功能將不可用)")
    
    # 檢查 requests
    try:
        import requests
        deps_status['requests'] = True
        print("✅ requests 已安裝")
    except ImportError:
        deps_status['requests'] = False
        print("⚠️  requests 未安裝 (FFmpeg 自動下載將不可用)")
    
    return deps_status

def install_missing_deps(missing_deps):
    """安裝缺失的依賴"""
    if not missing_deps:
        return True
    
    print(f"\n🔧 發現缺失的依賴: {', '.join(missing_deps)}")
    
    try:
        response = input("是否要自動安裝？(y/n): ").lower().strip()
        if response in ['y', 'yes', '是']:
            import subprocess
            
            for dep in missing_deps:
                print(f"正在安裝 {dep}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
                    print(f"✅ {dep} 安裝成功")
                except subprocess.CalledProcessError:
                    print(f"❌ {dep} 安裝失敗")
                    return False
            
            print("✅ 所有依賴安裝完成")
            return True
        else:
            print("跳過依賴安裝")
            return False
    except KeyboardInterrupt:
        print("\n用戶取消安裝")
        return False

def choose_startup_mode(deps_status):
    """選擇啟動模式"""
    print("\n🚀 選擇啟動模式:")
    
    if all(deps_status.values()):
        print("1. 完整版 (推薦) - 所有功能可用")
        print("2. 簡化版 - 基本 GUI 功能")
        print("3. 測試模式 - 運行測試套件")
        
        try:
            choice = input("\n請選擇 (1-3, 默認 1): ").strip()
            if choice == "2":
                return "simple"
            elif choice == "3":
                return "test"
            else:
                return "full"
        except KeyboardInterrupt:
            return None
    else:
        missing = [dep for dep, status in deps_status.items() if not status]
        print(f"由於缺少依賴 ({', '.join(missing)})，建議使用:")
        print("1. 簡化版 - 基本 GUI 功能")
        print("2. 測試模式 - 檢查問題")
        print("3. 完整版 - 嘗試運行 (可能出錯)")
        
        try:
            choice = input("\n請選擇 (1-3, 默認 1): ").strip()
            if choice == "2":
                return "test"
            elif choice == "3":
                return "full"
            else:
                return "simple"
        except KeyboardInterrupt:
            return None

def run_application(mode):
    """運行應用程式"""
    print(f"\n🎯 啟動 {mode} 模式...")
    
    try:
        if mode == "full":
            print("正在啟動完整版...")
            import main
            main.main()
            
        elif mode == "simple":
            print("正在啟動簡化版...")
            import simple_main
            simple_main.main()
            
        elif mode == "test":
            print("正在運行測試...")
            import run_tests
            run_tests.main()
            
        return True
        
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        print("\n🔧 建議:")
        print("1. 檢查依賴: python check_dependencies.py")
        print("2. 安裝依賴: python install_deps.py")
        print("3. 運行測試: python run_tests.py")
        
        import traceback
        print(f"\n詳細錯誤信息:")
        traceback.print_exc()
        return False

def main():
    """主函數"""
    print("🎬 YouTube 下載器")
    print("=" * 50)
    
    # 檢查基本環境
    if not check_environment():
        print("\n❌ 環境檢查失敗，無法運行")
        input("按 Enter 鍵退出...")
        return False
    
    # 檢查依賴
    deps_status = check_dependencies()
    
    # 處理缺失的依賴
    missing_deps = [dep for dep, status in deps_status.items() if not status]
    if missing_deps:
        if not install_missing_deps(missing_deps):
            print("⚠️  部分功能可能不可用")
    
    # 重新檢查依賴狀態
    deps_status = check_dependencies()
    
    # 選擇啟動模式
    mode = choose_startup_mode(deps_status)
    if mode is None:
        print("\n👋 用戶取消，退出程式")
        return False
    
    # 運行應用程式
    success = run_application(mode)
    
    if success:
        print("\n✅ 程式正常結束")
    else:
        print("\n❌ 程式異常結束")
        input("按 Enter 鍵退出...")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 用戶中斷，程式退出")
    except Exception as e:
        print(f"\n💥 未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        input("按 Enter 鍵退出...")