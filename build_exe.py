#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 影片下載器 EXE 打包腳本
YouTube Video Downloader EXE Build Script
YouTube動画ダウンローダー EXE ビルドスクリプト
YouTube 비디오 다운로더 EXE 빌드 스크립트

版本 / Version / バージョン / 버전: V1.0
"""

import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def print_banner():
    """顯示打包橫幅"""
    print("=" * 60)
    print("🎬 YouTube 影片下載器 EXE 打包工具")
    print("🎬 YouTube Video Downloader EXE Builder")
    print("🎬 YouTube動画ダウンローダー EXE ビルダー")
    print("🎬 YouTube 비디오 다운로더 EXE 빌더")
    print("=" * 60)
    print(f"版本 / Version / バージョン / 버전: V1.0")
    print(f"作業系統 / OS / OS / OS: {platform.system()} {platform.release()}")
    print("=" * 60)

def check_dependencies():
    """檢查依賴套件"""
    print("🔍 檢查依賴套件 / Checking Dependencies...")
    
    required_packages = [
        'PyQt6', 'PySide6', 'PyInstaller', 'yt_dlp', 'certifi', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - 已安裝 / Installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 未安裝 / Not Installed")
    
    if missing_packages:
        print(f"\n⚠️ 缺少套件 / Missing packages: {', '.join(missing_packages)}")
        print("請運行: python install_dependencies.py")
        return False
    
    print("✅ 所有依賴套件已安裝 / All dependencies installed")
    return True

def create_spec_file(version="V1.0"):
    """創建 PyInstaller spec 文件"""
    print("📝 創建 PyInstaller spec 文件...")
    
    # PyQt6 版本 spec
    pyqt6_spec = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/user_preferences.json', 'src'),
        ('VERSION', '.'),
        ('README.md', '.'),
        ('使用說明.md', '.'),
        ('執行說明.md', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'yt_dlp',
        'certifi',
        'requests',
        'urllib3',
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube下載器_PyQt6_{version}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    # PySide6 版本 spec
    pyside6_spec = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main_pyside.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/user_preferences.json', 'src'),
        ('VERSION', '.'),
        ('README.md', '.'),
        ('使用說明.md', '.'),
        ('執行說明.md', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'yt_dlp',
        'certifi',
        'requests',
        'urllib3',
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube下載器_PySide6_{version}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    # 簡化版本 spec
    simple_spec = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/simple_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/user_preferences.json', 'src'),
        ('VERSION', '.'),
        ('README.md', '.'),
        ('使用說明.md', '.'),
        ('執行說明.md', '.'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'yt_dlp',
        'certifi',
        'requests',
        'urllib3',
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube下載器_簡化版_{version}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    # 命令行版本 spec
    cli_spec = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/cli_downloader.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/user_preferences.json', 'src'),
        ('VERSION', '.'),
        ('README.md', '.'),
        ('使用說明.md', '.'),
        ('執行說明.md', '.'),
    ],
    hiddenimports=[
        'yt_dlp',
        'certifi',
        'requests',
        'urllib3',
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='YouTube下載器_CLI_{version}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
'''
    
    # 寫入 spec 文件
    with open('youtube_downloader_pyqt6.spec', 'w', encoding='utf-8') as f:
        f.write(pyqt6_spec)
    
    with open('youtube_downloader_pyside6.spec', 'w', encoding='utf-8') as f:
        f.write(pyside6_spec)
    
    with open('youtube_downloader_simple.spec', 'w', encoding='utf-8') as f:
        f.write(simple_spec)
    
    with open('youtube_downloader_cli.spec', 'w', encoding='utf-8') as f:
        f.write(cli_spec)
    
    print("✅ Spec 文件創建完成")

def build_exe(version="V1.0"):
    """執行打包"""
    print("🔨 開始打包 EXE 文件...")
    
    # 創建輸出目錄
    output_dir = f"dist/YouTube下載器_{version}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 打包選項
    build_options = [
        {
            'name': 'PyQt6 版本',
            'spec': 'youtube_downloader_pyqt6.spec',
            'exe_name': f'YouTube下載器_PyQt6_{version}.exe'
        },
        {
            'name': 'PySide6 版本 (推薦)',
            'spec': 'youtube_downloader_pyside6.spec', 
            'exe_name': f'YouTube下載器_PySide6_{version}.exe'
        },
        {
            'name': '簡化版本',
            'spec': 'youtube_downloader_simple.spec',
            'exe_name': f'YouTube下載器_簡化版_{version}.exe'
        },
        {
            'name': '命令行版本',
            'spec': 'youtube_downloader_cli.spec',
            'exe_name': f'YouTube下載器_CLI_{version}.exe'
        }
    ]
    
    success_count = 0
    
    for option in build_options:
        print(f"\n🔨 打包 {option['name']}...")
        try:
            # 執行 PyInstaller
            cmd = ['pyinstaller', '--clean', option['spec']]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode == 0:
                print(f"✅ {option['name']} 打包成功")
                
                # 移動到輸出目錄
                src_path = f"dist/{option['exe_name']}"
                dst_path = f"{output_dir}/{option['exe_name']}"
                
                if os.path.exists(src_path):
                    shutil.move(src_path, dst_path)
                    print(f"📁 移動到: {dst_path}")
                    success_count += 1
                else:
                    print(f"⚠️ 找不到輸出文件: {src_path}")
            else:
                print(f"❌ {option['name']} 打包失敗")
                print(f"錯誤信息: {result.stderr}")
                
        except Exception as e:
            print(f"❌ {option['name']} 打包異常: {str(e)}")
    
    return success_count, output_dir

def create_installer_script(output_dir, version="V1.0"):
    """創建安裝腳本"""
    print("📝 創建安裝腳本...")
    
    installer_script = f'''@echo off
chcp 65001 >nul
echo ========================================
echo YouTube 影片下載器 V{version} 安裝腳本
echo YouTube Video Downloader V{version} Installer
echo ========================================
echo.

echo 正在安裝 YouTube 影片下載器...
echo Installing YouTube Video Downloader...

REM 創建桌面快捷方式
echo 創建桌面快捷方式...
if exist "%USERPROFILE%\\Desktop" (
    echo @echo off > "%USERPROFILE%\\Desktop\\YouTube下載器_PySide6_{version}.bat"
    echo cd /d "%~dp0" >> "%USERPROFILE%\\Desktop\\YouTube下載器_PySide6_{version}.bat"
    echo start "" "%~dp0\\YouTube下載器_PySide6_{version}.exe" >> "%USERPROFILE%\\Desktop\\YouTube下載器_PySide6_{version}.bat"
    echo 桌面快捷方式創建完成
) else (
    echo 找不到桌面目錄，跳過快捷方式創建
)

echo.
echo 安裝完成！請選擇要運行的版本：
echo Installation complete! Please choose version to run:
echo.
echo 1. PySide6 版本 (推薦 / Recommended)
echo 2. PyQt6 版本
echo 3. 簡化版本 / Simple Version
echo 4. 命令行版本 / CLI Version
echo 5. 退出 / Exit
echo.

set /p choice="請選擇 / Please choose (1-5): "

if "%choice%"=="1" (
    start "" "YouTube下載器_PySide6_{version}.exe"
) else if "%choice%"=="2" (
    start "" "YouTube下載器_PyQt6_{version}.exe"
) else if "%choice%"=="3" (
    start "" "YouTube下載器_簡化版_{version}.exe"
) else if "%choice%"=="4" (
    start "" "YouTube下載器_CLI_{version}.exe"
) else if "%choice%"=="5" (
    echo 退出安裝程序
    exit
) else (
    echo 無效選擇，退出
    exit
)

pause
'''
    
    installer_path = f"{output_dir}/安裝_YouTube下載器_{version}.bat"
    with open(installer_path, 'w', encoding='utf-8') as f:
        f.write(installer_script)
    
    print(f"✅ 安裝腳本創建完成: {installer_path}")

def copy_documentation(output_dir, version="V1.0"):
    """複製文檔文件"""
    print("📋 複製文檔文件...")
    
    docs = [
        'README.md',
        '使用說明.md', 
        '執行說明.md',
        'VERSION',
        'CHANGELOG.md',
        'RELEASE_NOTES_V1.0.md'
    ]
    
    for doc in docs:
        if os.path.exists(doc):
            shutil.copy2(doc, output_dir)
            print(f"📄 複製: {doc}")
    
    print("✅ 文檔複製完成")

def create_readme_exe(output_dir, version="V1.0"):
    """創建 EXE 版本說明文件"""
    print("📝 創建 EXE 版本說明...")
    
    exe_readme = f'''# YouTube 影片下載器 V{version} - EXE 版本

## 🎉 歡迎使用 YouTube 影片下載器！

### 📁 文件說明

#### 主要執行檔 / Main Executables
- **YouTube下載器_PySide6_{version}.exe** - PySide6 版本 (推薦使用)
- **YouTube下載器_PyQt6_{version}.exe** - PyQt6 版本
- **YouTube下載器_簡化版_{version}.exe** - 簡化 GUI 版本
- **YouTube下載器_CLI_{version}.exe** - 命令行版本

#### 安裝腳本 / Installer
- **安裝_YouTube下載器_{version}.bat** - 自動安裝腳本

### 🚀 快速開始

1. **推薦使用**: 雙擊 `YouTube下載器_PySide6_{version}.exe`
2. **如果遇到問題**: 嘗試 `YouTube下載器_簡化版_{version}.exe`
3. **進階用戶**: 使用 `YouTube下載器_CLI_{version}.exe`

### ⚠️ 注意事項

- 首次運行可能需要較長時間載入
- 確保網路連接正常
- 如果出現 SSL 錯誤，請更新系統時間
- 某些防毒軟體可能會誤報，請添加信任

### 🔧 故障排除

1. **無法啟動**: 嘗試以管理員身份運行
2. **下載失敗**: 檢查網路連接和 URL 格式
3. **SSL 錯誤**: 更新系統時間和證書
4. **檔案名稱錯誤**: 更新 yt-dlp 和 certifi

### 📞 技術支援

如有問題，請查看：
- `使用說明.md` - 詳細使用說明
- `執行說明.md` - 執行和故障排除
- `CHANGELOG.md` - 版本變更記錄

### 🌍 多語言支援

本軟體支援以下語言：
- 中文 (繁體)
- English
- 日本語  
- 한국어

---

**版本 V{version} - 2024年12月19日**
**僅供個人學習和研究使用**
'''
    
    readme_path = f"{output_dir}/EXE版本說明.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(exe_readme)
    
    print(f"✅ EXE 版本說明創建完成: {readme_path}")

def cleanup():
    """清理臨時文件"""
    print("🧹 清理臨時文件...")
    
    # 清理 build 目錄
    if os.path.exists('build'):
        shutil.rmtree('build')
        print("🗑️ 清理 build 目錄")
    
    # 清理 spec 文件
    spec_files = [
        'youtube_downloader_pyqt6.spec',
        'youtube_downloader_pyside6.spec', 
        'youtube_downloader_simple.spec',
        'youtube_downloader_cli.spec'
    ]
    
    for spec in spec_files:
        if os.path.exists(spec):
            os.remove(spec)
            print(f"🗑️ 清理: {spec}")
    
    # 清理 dist 目錄中的臨時文件
    if os.path.exists('dist'):
        for item in os.listdir('dist'):
            if not item.startswith('YouTube下載器_'):
                item_path = os.path.join('dist', item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
    
    print("✅ 清理完成")

def main():
    """主函數"""
    print_banner()
    
    # 檢查依賴
    if not check_dependencies():
        print("\n❌ 依賴檢查失敗，請先安裝所需套件")
        return
    
    # 獲取版本號
    version = "V1.0"
    if os.path.exists('VERSION'):
        with open('VERSION', 'r', encoding='utf-8') as f:
            version = f.readline().strip()
    
    print(f"\n🎯 目標版本: {version}")
    
    try:
        # 創建 spec 文件
        create_spec_file(version)
        
        # 執行打包
        success_count, output_dir = build_exe(version)
        
        if success_count > 0:
            print(f"\n🎉 打包完成！成功打包 {success_count} 個版本")
            
            # 創建安裝腳本
            create_installer_script(output_dir, version)
            
            # 複製文檔
            copy_documentation(output_dir, version)
            
            # 創建說明文件
            create_readme_exe(output_dir, version)
            
            print(f"\n📁 輸出目錄: {output_dir}")
            print("📋 包含文件:")
            
            if os.path.exists(output_dir):
                for item in os.listdir(output_dir):
                    print(f"  - {item}")
            
            print(f"\n✅ 所有文件已準備就緒！")
            print(f"🚀 請運行: {output_dir}/安裝_YouTube下載器_{version}.bat")
            
        else:
            print("\n❌ 打包失敗，沒有成功創建任何 EXE 文件")
            
    except Exception as e:
        print(f"\n❌ 打包過程發生錯誤: {str(e)}")
        
    finally:
        # 清理臨時文件
        cleanup()
    
    print("\n" + "=" * 60)
    print("🎬 YouTube 影片下載器 EXE 打包完成")
    print("🎬 YouTube Video Downloader EXE Build Complete")
    print("🎬 YouTube動画ダウンローダー EXE ビルド完了")
    print("🎬 YouTube 비디오 다운로더 EXE 빌드 완료")
    print("=" * 60)

if __name__ == "__main__":
    main() 