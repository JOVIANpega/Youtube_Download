#!/usr/bin/env python3
"""
YouTube 下載器依賴安裝腳本
Dependency Installation Script for YouTube Downloader
YouTubeダウンローダー依存関係インストールスクリプト
유튜브 다운로더 의존성 설치 스크립트
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """執行命令並顯示結果"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} 成功")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"✗ {description} 失敗")
            if result.stderr:
                print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ {description} 錯誤: {e}")
        return False
    return True

def check_ffmpeg():
    """檢查 FFmpeg 是否已安裝"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def install_ffmpeg():
    """安裝 FFmpeg"""
    system = platform.system().lower()
    
    if system == "windows":
        print("\n在 Windows 上安裝 FFmpeg:")
        print("1. 請訪問 https://ffmpeg.org/download.html")
        print("2. 下載 Windows 版本")
        print("3. 解壓縮到 C:\\ffmpeg")
        print("4. 將 C:\\ffmpeg\\bin 添加到系統 PATH")
        print("\n或者使用 Chocolatey (如果已安裝):")
        print("choco install ffmpeg")
        
    elif system == "darwin":  # macOS
        print("\n在 macOS 上安裝 FFmpeg:")
        print("使用 Homebrew:")
        print("brew install ffmpeg")
        
    elif system == "linux":
        print("\n在 Linux 上安裝 FFmpeg:")
        print("Ubuntu/Debian:")
        print("sudo apt update && sudo apt install ffmpeg")
        print("\nCentOS/RHEL/Fedora:")
        print("sudo yum install ffmpeg")
        print("或")
        print("sudo dnf install ffmpeg")

def main():
    print("YouTube 下載器依賴安裝程序")
    print("=" * 50)
    
    # 檢查 Python 版本
    if sys.version_info < (3, 7):
        print("錯誤: 需要 Python 3.7 或更高版本")
        return
    
    print(f"Python 版本: {sys.version}")
    
    # 安裝 Python 依賴
    print("\n安裝 Python 依賴...")
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "安裝 Python 依賴"
    )
    
    if not success:
        print("\n嘗試升級 pip...")
        run_command(f"{sys.executable} -m pip install --upgrade pip", "升級 pip")
        run_command(
            f"{sys.executable} -m pip install -r requirements.txt",
            "重新安裝 Python 依賴"
        )
    
    # 檢查 FFmpeg
    print("\n檢查 FFmpeg...")
    if check_ffmpeg():
        print("✓ FFmpeg 已安裝")
    else:
        print("✗ FFmpeg 未安裝")
        install_ffmpeg()
        print("\n請安裝 FFmpeg 後重新運行此腳本")
    
    print("\n安裝完成！")
    print("\n使用方法:")
    print("python src/main.py")

if __name__ == "__main__":
    main() 