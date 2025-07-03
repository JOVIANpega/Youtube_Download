#!/usr/bin/env python3
"""
YouTube下載器 V1.63 打包腳本
使用PyInstaller創建獨立執行檔
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# 顯示打包信息
print("=" * 60)
print("YouTube下載器 V1.63 打包腳本")
print("=" * 60)

# 檢查必要的模組
try:
    import PyInstaller
    print("✓ 已安裝 PyInstaller")
except ImportError:
    print("✗ 未安裝 PyInstaller，正在安裝...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    print("✓ PyInstaller 安裝完成")

# 確保在正確的目錄中
script_dir = Path(__file__).parent.absolute()
os.chdir(script_dir)
print(f"✓ 工作目錄: {script_dir}")

# 創建臨時目錄
temp_dir = script_dir / "build_temp"
if temp_dir.exists():
    shutil.rmtree(temp_dir)
temp_dir.mkdir(exist_ok=True)
print(f"✓ 創建臨時目錄: {temp_dir}")

# 複製版本信息
version_file = script_dir / "version_info.txt"
if version_file.exists():
    shutil.copy(version_file, temp_dir / "version_info.txt")
    print(f"✓ 複製版本信息: {version_file}")
else:
    print(f"✗ 版本信息文件不存在: {version_file}")

# 複製FFmpeg
ffmpeg_dir = script_dir / "ffmpeg_bin"
if ffmpeg_dir.exists():
    ffmpeg_temp_dir = temp_dir / "ffmpeg_bin"
    shutil.copytree(ffmpeg_dir, ffmpeg_temp_dir)
    print(f"✓ 複製FFmpeg: {ffmpeg_dir}")
else:
    print(f"✗ FFmpeg目錄不存在: {ffmpeg_dir}")

# 準備打包命令
start_script = script_dir / "start_downloader_v1.63.py"
if not start_script.exists():
    # 創建啟動腳本
    print(f"✗ 啟動腳本不存在，正在創建: {start_script}")
    with open(start_script, "w", encoding="utf-8") as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
YouTube下載器 V1.63 啟動腳本
\"\"\"

import os
import sys
from pathlib import Path

# 添加src目錄到路徑
script_dir = Path(__file__).parent.absolute()
src_dir = script_dir / "src"
sys.path.insert(0, str(src_dir))

# 導入主模組
try:
    from tabbed_gui_demo import main
    main()
except ImportError as e:
    print(f"錯誤: 無法導入主模組: {e}")
    input("按Enter鍵退出...")
    sys.exit(1)
except Exception as e:
    print(f"錯誤: {e}")
    import traceback
    traceback.print_exc()
    input("按Enter鍵退出...")
    sys.exit(1)
""")
    print(f"✓ 創建啟動腳本: {start_script}")

# 創建PyInstaller規格文件
spec_file = temp_dir / "youtube_downloader_v1.63.spec"
with open(spec_file, "w", encoding="utf-8") as f:
    f.write(f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{start_script.as_posix()}'],
    pathex=['{script_dir.as_posix()}'],
    binaries=[],
    datas=[
        ('{(script_dir / "src").as_posix()}', 'src'),
        ('{(script_dir / "ffmpeg_bin").as_posix()}', 'ffmpeg_bin'),
        ('{(script_dir / "VERSION").as_posix()}', '.'),
        ('{(script_dir / "RELEASE_NOTES_V1.63.md").as_posix()}', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'yt_dlp',
        'yt_dlp.extractor',
        'ssl',
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
    name='youtube_downloader_v1.63',
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
    icon='{(script_dir / "src" / "ui" / "icon.ico").as_posix() if (script_dir / "src" / "ui" / "icon.ico").exists() else None}',
    version='{(temp_dir / "version_info.txt").as_posix() if (temp_dir / "version_info.txt").exists() else None}',
)
""")
print(f"✓ 創建PyInstaller規格文件: {spec_file}")

# 運行PyInstaller
print("\n開始打包...")
cmd = [
    sys.executable, 
    "-m", "PyInstaller", 
    "--clean",
    "--distpath", str(script_dir / "dist"),
    "--workpath", str(temp_dir),
    str(spec_file)
]
print(f"執行命令: {' '.join(cmd)}")
subprocess.run(cmd, check=True)

# 檢查結果
exe_file = script_dir / "dist" / "youtube_downloader_v1.63.exe"
if exe_file.exists():
    print(f"\n✓ 打包成功! 輸出文件: {exe_file}")
    
    # 創建發布ZIP
    import zipfile
    zip_file = script_dir / "youtube_downloader_v1.63.zip"
    with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(exe_file, exe_file.name)
        zipf.write(script_dir / "RELEASE_NOTES_V1.63.md", "RELEASE_NOTES.md")
        zipf.write(script_dir / "VERSION", "VERSION")
        
        # 添加其他必要文件
        if (script_dir / "README.md").exists():
            zipf.write(script_dir / "README.md", "README.md")
        if (script_dir / "LICENSE").exists():
            zipf.write(script_dir / "LICENSE", "LICENSE")
            
    print(f"✓ 創建發布ZIP: {zip_file}")
else:
    print(f"\n✗ 打包失敗! 未找到輸出文件: {exe_file}")

# 清理臨時文件
print("\n清理臨時文件...")
if temp_dir.exists():
    shutil.rmtree(temp_dir)
print("✓ 清理完成")

print("\n" + "=" * 60)
print("打包過程完成!")
print("=" * 60) 