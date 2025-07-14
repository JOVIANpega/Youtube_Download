import os
import sys
from src.tabbed_gui_demo import main

if __name__ == "__main__":
    # 設置版本號
    os.environ["APP_VERSION"] = "1.72"
    
    # 檢查是否是打包後的環境
    if getattr(sys, 'frozen', False):
        # 設置資源路徑
        os.environ["RESOURCE_PATH"] = os.path.join(sys._MEIPASS, "assets")
        os.environ["FFMPEG_PATH"] = os.path.join(sys._MEIPASS, "ffmpeg_bin")
    else:
        # 開發環境
        os.environ["RESOURCE_PATH"] = "assets"
        os.environ["FFMPEG_PATH"] = "ffmpeg_bin"
    
    # 啟動主程序
    main() 