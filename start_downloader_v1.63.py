#!/usr/bin/env python3
"""
YouTube下載器 V1.63 啟動腳本
"""

import os
import sys
import ssl
from pathlib import Path

# 添加src目錄到路徑
script_dir = Path(__file__).parent.absolute()
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# SSL修復
def apply_ssl_fix():
    """應用SSL修復"""
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl._create_default_https_context = lambda: ssl_context
        print("[SSL] 已停用SSL證書驗證，這可以解決某些SSL錯誤")
        return True
    except Exception as e:
        print(f"[SSL] 修復遇到問題: {e}")
        return False

# 應用SSL修復
apply_ssl_fix()

# 顯示啟動信息
print("YouTube 下載器啟動器")
print("=" * 50)

# 檢查PySide6是否可用
try:
    import PySide6
    print("✓ 檢測到 PySide6，可以使用 GUI 模式")
    has_gui = True
except ImportError:
    print("✗ 未檢測到 PySide6，僅可使用命令行模式")
    has_gui = False

# 選擇啟動模式
print("選擇啟動模式:")
print("1. GUI 模式 (圖形介面)")
print("2. 命令行模式")
print("3. 退出")

while True:
    try:
        choice = input("請選擇 (1-3): ")
        if choice == "1":
            if has_gui:
                try:
                    from tabbed_gui_demo import main
                    main()
                    break
                except ImportError as e:
                    print(f"錯誤: 無法導入GUI模組: {e}")
                    input("按Enter鍵繼續...")
                except Exception as e:
                    print(f"錯誤: {e}")
                    import traceback
                    traceback.print_exc()
                    input("按Enter鍵繼續...")
            else:
                print("錯誤: 未安裝PySide6，無法使用GUI模式")
                print("提示: 請執行 'pip install PySide6' 安裝必要的庫")
                input("按Enter鍵繼續...")
        elif choice == "2":
            try:
                from cli_downloader import main as cli_main
                cli_main()
                break
            except ImportError as e:
                print(f"錯誤: 無法導入命令行模組: {e}")
                input("按Enter鍵繼續...")
            except Exception as e:
                print(f"錯誤: {e}")
                import traceback
                traceback.print_exc()
                input("按Enter鍵繼續...")
        elif choice == "3":
            print("感謝使用，再見!")
            sys.exit(0)
        else:
            print("錯誤: 請輸入1-3之間的數字")
    except KeyboardInterrupt:
        print("\n已取消")
        sys.exit(0)
    except Exception as e:
        print(f"發生錯誤: {e}")
        input("按Enter鍵繼續...")

# 如果執行到這裡，說明程序已經結束
print("程序已結束") 