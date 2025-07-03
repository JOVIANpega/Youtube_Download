#!/usr/bin/env python3
"""
YouTube 下載器啟動腳本 V1.61
YouTube Downloader Launcher V1.61
YouTubeダウンローダー起動スクリプト V1.61
유튜브 다운로더 실행 스크립트 V1.61
"""

import sys
import os
import subprocess
import traceback
import datetime

def log(message):
    """輸出日誌"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
    
    # 保存到日誌檔案
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        log_file = os.path.join(log_dir, f"launcher_{datetime.datetime.now().strftime('%Y-%m-%d')}.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"無法寫入日誌檔案: {str(e)}")

def check_gui_available():
    """檢查 GUI 是否可用"""
    log("檢查GUI庫可用性...")
    try:
        # 嘗試 PySide6
        import PySide6
        log("✓ 成功導入 PySide6")
        return "PySide6"
    except ImportError:
        log("✗ 無法導入 PySide6")
        try:
            # 嘗試 PyQt6
            import PyQt6
            log("✓ 成功導入 PyQt6")
            return "PyQt6"
        except ImportError:
            log("✗ 無法導入 PyQt6")
            return None

def launch_tabbed_gui():
    """啟動標籤式GUI"""
    log("嘗試啟動標籤式GUI...")
    try:
        # 檢查文件是否存在
        if os.path.exists("src/tabbed_gui_demo.py"):
            log("找到標籤式GUI文件，正在啟動...")
            # 直接導入並執行
            try:
                # 添加src目錄到路徑
                sys.path.append("src")
                import tabbed_gui_demo
                log("成功導入標籤式GUI模塊")
                tabbed_gui_demo.main()
                return True
            except Exception as e:
                log(f"導入標籤式GUI模塊失敗: {str(e)}")
                log(traceback.format_exc())
                # 嘗試使用subprocess運行
                try:
                    log("嘗試使用subprocess運行標籤式GUI...")
                    subprocess.run([sys.executable, "src/tabbed_gui_demo.py"])
                    return True
                except Exception as e2:
                    log(f"使用subprocess運行標籤式GUI失敗: {str(e2)}")
                    return False
        else:
            log("標籤式GUI文件不存在")
            return False
    except Exception as e:
        log(f"啟動標籤式GUI時發生錯誤: {str(e)}")
        log(traceback.format_exc())
        return False

def launch_pyside_gui():
    """啟動PySide GUI"""
    log("嘗試啟動PySide GUI...")
    try:
        # 檢查文件是否存在
        if os.path.exists("src/main_pyside.py"):
            log("找到PySide GUI文件，正在啟動...")
            # 直接導入並執行
            try:
                # 添加src目錄到路徑
                sys.path.append("src")
                import main_pyside
                log("成功導入PySide GUI模塊")
                main_pyside.main()
                return True
            except Exception as e:
                log(f"導入PySide GUI模塊失敗: {str(e)}")
                log(traceback.format_exc())
                # 嘗試使用subprocess運行
                try:
                    log("嘗試使用subprocess運行PySide GUI...")
                    subprocess.run([sys.executable, "src/main_pyside.py"])
                    return True
                except Exception as e2:
                    log(f"使用subprocess運行PySide GUI失敗: {str(e2)}")
                    return False
        else:
            log("PySide GUI文件不存在")
            return False
    except Exception as e:
        log(f"啟動PySide GUI時發生錯誤: {str(e)}")
        log(traceback.format_exc())
        return False

def launch_pyqt_gui():
    """啟動PyQt GUI"""
    log("嘗試啟動PyQt GUI...")
    try:
        # 檢查文件是否存在
        if os.path.exists("src/main.py"):
            log("找到PyQt GUI文件，正在啟動...")
            # 直接導入並執行
            try:
                # 添加src目錄到路徑
                sys.path.append("src")
                import main
                log("成功導入PyQt GUI模塊")
                main.main()
                return True
            except Exception as e:
                log(f"導入PyQt GUI模塊失敗: {str(e)}")
                log(traceback.format_exc())
                # 嘗試使用subprocess運行
                try:
                    log("嘗試使用subprocess運行PyQt GUI...")
                    subprocess.run([sys.executable, "src/main.py"])
                    return True
                except Exception as e2:
                    log(f"使用subprocess運行PyQt GUI失敗: {str(e2)}")
                    return False
        else:
            log("PyQt GUI文件不存在")
            return False
    except Exception as e:
        log(f"啟動PyQt GUI時發生錯誤: {str(e)}")
        log(traceback.format_exc())
        return False

def main():
    """主函數"""
    log("===== YouTube下載器啟動器 V1.61 =====")
    
    # 顯示當前工作目錄
    log(f"當前工作目錄: {os.getcwd()}")
    
    # 列出src目錄中的文件
    try:
        if os.path.exists("src"):
            log("src目錄內容:")
            for item in os.listdir("src"):
                log(f"  - {item}")
        else:
            log("警告: src目錄不存在")
    except Exception as e:
        log(f"列出src目錄內容時發生錯誤: {str(e)}")
    
    # 檢查是否有命令行參數
    if len(sys.argv) > 1:
        # 直接使用命令行版本
        log("使用命令行模式...")
        try:
            subprocess.run([sys.executable, "src/cli_downloader.py"] + sys.argv[1:])
        except Exception as e:
            log(f"執行命令行模式失敗: {str(e)}")
            log(traceback.format_exc())
        return
    
    # 檢查 GUI 可用性
    gui_type = check_gui_available()
    
    if gui_type:
        log(f"✓ 檢測到 {gui_type}，啟動 GUI 模式")
        
        # 嘗試啟動標籤式GUI
        if launch_tabbed_gui():
            log("標籤式GUI啟動成功")
            return
        
        # 如果標籤式GUI啟動失敗，嘗試啟動PySide GUI
        if gui_type == "PySide6" and launch_pyside_gui():
            log("PySide GUI啟動成功")
            return
        
        # 如果PySide GUI啟動失敗，嘗試啟動PyQt GUI
        if launch_pyqt_gui():
            log("PyQt GUI啟動成功")
            return
        
        # 所有GUI啟動嘗試都失敗
        log("所有GUI啟動嘗試都失敗")
    else:
        log("⚠️  未檢測到 GUI 庫，無法啟動")
        log("請確保已安裝 PySide6 或 PyQt6")
    
    # 在GUI啟動失敗的情況下，顯示錯誤消息並等待用戶按鍵
    print("\n錯誤: 無法啟動GUI界面")
    print("請確保已正確安裝所有依賴，並且src目錄包含必要的GUI文件")
    print("\n按任意鍵退出...")
    
    # 使用os.system而不是input()，避免在打包後出現問題
    os.system("pause")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"啟動器發生嚴重錯誤: {str(e)}")
        print(traceback.format_exc())
        print("\n按任意鍵退出...")
        os.system("pause") 