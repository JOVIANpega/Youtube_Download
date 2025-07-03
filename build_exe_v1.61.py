#!/usr/bin/env python3
"""
YouTube 下載器 - 打包腳本 V1.61
用於打包YouTube下載器為獨立可執行文件
"""

import os
import sys
import shutil
import subprocess
import PyInstaller.__main__
import datetime

def log(message):
    """輸出日誌"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_dependencies():
    """檢查依賴"""
    try:
        import PyInstaller
        import PySide6
        import yt_dlp
        log("所有必要依賴已安裝")
        return True
    except ImportError as e:
        log(f"缺少依賴: {e}")
        log("請執行 install_dependencies.py 安裝所有依賴")
        return False

def clean_build_folders():
    """清理構建文件夾"""
    folders_to_clean = ["build", "dist/YouTube下載器V1.61"]
    for folder in folders_to_clean:
        if os.path.exists(folder):
            log(f"清理文件夾: {folder}")
            try:
                shutil.rmtree(folder)
            except Exception as e:
                log(f"清理失敗: {e}")

def copy_ffmpeg():
    """複製FFmpeg到打包目錄"""
    ffmpeg_dir = "ffmpeg_bin"
    target_dir = "dist/YouTube下載器V1.61/ffmpeg_bin"
    
    if not os.path.exists(ffmpeg_dir):
        log("錯誤: ffmpeg_bin 目錄不存在")
        return False
    
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # 複製FFmpeg文件
        for file in os.listdir(ffmpeg_dir):
            if file.endswith(".exe") or file.endswith(".dll"):
                source = os.path.join(ffmpeg_dir, file)
                target = os.path.join(target_dir, file)
                shutil.copy2(source, target)
                log(f"已複製: {file}")
        
        return True
    except Exception as e:
        log(f"複製FFmpeg失敗: {e}")
        return False

def copy_docs():
    """複製文檔文件"""
    docs = ["README.md", "使用說明.md", "執行說明.md", "RELEASE_NOTES_V1.61.md", "VERSION"]
    target_dir = "dist/YouTube下載器V1.61"
    
    try:
        for doc in docs:
            if os.path.exists(doc):
                target = os.path.join(target_dir, doc)
                shutil.copy2(doc, target)
                log(f"已複製: {doc}")
        return True
    except Exception as e:
        log(f"複製文檔失敗: {e}")
        return False

def copy_src_files():
    """複製源代碼文件"""
    src_dir = "src"
    target_dir = "dist/YouTube下載器V1.61/src"
    
    try:
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        
        # 複製所有Python文件
        for root, dirs, files in os.walk(src_dir):
            for file in files:
                if file.endswith(".py"):
                    rel_path = os.path.relpath(os.path.join(root, file), src_dir)
                    target_file = os.path.join(target_dir, rel_path)
                    target_folder = os.path.dirname(target_file)
                    
                    if not os.path.exists(target_folder):
                        os.makedirs(target_folder)
                        
                    shutil.copy2(os.path.join(root, file), target_file)
                    log(f"已複製源文件: {rel_path}")
        
        # 複製UI文件夾中的圖標和其他資源
        ui_dir = os.path.join(src_dir, "ui")
        if os.path.exists(ui_dir):
            target_ui_dir = os.path.join(target_dir, "ui")
            if not os.path.exists(target_ui_dir):
                os.makedirs(target_ui_dir)
                
            for root, dirs, files in os.walk(ui_dir):
                for file in files:
                    if file.endswith((".ico", ".png", ".jpg")):
                        rel_path = os.path.relpath(os.path.join(root, file), ui_dir)
                        target_file = os.path.join(target_ui_dir, rel_path)
                        target_folder = os.path.dirname(target_file)
                        
                        if not os.path.exists(target_folder):
                            os.makedirs(target_folder)
                            
                        shutil.copy2(os.path.join(root, file), target_file)
                        log(f"已複製資源文件: ui/{rel_path}")
        
        return True
    except Exception as e:
        log(f"複製源文件失敗: {e}")
        return False

def build_exe():
    """構建可執行文件"""
    log("開始構建可執行文件...")
    
    # 設定打包參數
    app_name = "YouTube下載器V1.61"
    main_script = "start_downloader_v1.61.py"  # 使用新的啟動腳本
    icon_file = "src/ui/icons/youtube.ico" if os.path.exists("src/ui/icons/youtube.ico") else None
    
    # 準備PyInstaller參數
    pyinstaller_args = [
        main_script,
        "--name=" + app_name,
        "--onedir",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--add-data=version_info.txt;.",
        "--add-data=src;src",  # 添加src目錄
        "--hidden-import=PySide6",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=yt_dlp",
        "--exclude-module=PyQt6",  # 排除PyQt6綁定
        "--exclude-module=PyQt5",  # 排除PyQt5綁定
    ]
    
    # 添加圖標（如果存在）
    if icon_file:
        pyinstaller_args.append(f"--icon={icon_file}")
    else:
        log("警告: 圖標文件不存在，使用默認圖標")
    
    # 添加版本信息
    if os.path.exists("version_info.txt"):
        pyinstaller_args.append("--version-file=version_info.txt")
    
    # 執行PyInstaller
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        log("構建完成")
        return True
    except Exception as e:
        log(f"構建失敗: {e}")
        return False

def main():
    """主函數"""
    log("===== YouTube下載器 V1.61 打包工具 =====")
    
    # 檢查依賴
    if not check_dependencies():
        return
    
    # 清理構建文件夾
    clean_build_folders()
    
    # 構建可執行文件
    if not build_exe():
        return
    
    # 複製FFmpeg
    if not copy_ffmpeg():
        log("警告: FFmpeg複製失敗，程序可能無法正常運行")
    
    # 複製文檔
    if not copy_docs():
        log("警告: 文檔複製失敗")
    
    # 複製源代碼文件
    if not copy_src_files():
        log("警告: 源代碼複製失敗，程序可能無法正常運行")
    
    log("===== 打包完成 =====")
    log(f"可執行文件位於: {os.path.abspath('dist/YouTube下載器V1.61/YouTube下載器V1.61.exe')}")

if __name__ == "__main__":
    main() 