import PyInstaller.__main__
import os
import shutil
import sys
import urllib.request
import zipfile
import platform

# 確保 ffmpeg_bin 目錄存在
if not os.path.exists('ffmpeg_bin'):
    os.makedirs('ffmpeg_bin')

# 下載 FFmpeg (如果不存在)
def download_ffmpeg():
    ffmpeg_path = os.path.join('ffmpeg_bin', 'ffmpeg.exe')
    if os.path.exists(ffmpeg_path) and os.path.getsize(ffmpeg_path) > 1000000:
        print(f"FFmpeg 已存在: {ffmpeg_path}")
        return
    
    print("正在下載 FFmpeg...")
    
    # Windows 版本 FFmpeg 下載
    url = "https://github.com/GyanD/codexffmpeg/releases/download/6.1.1/ffmpeg-6.1.1-essentials_build.zip"
    zip_path = os.path.join('ffmpeg_bin', "ffmpeg.zip")
    
    # 下載 FFmpeg
    try:
        print(f"從 {url} 下載 FFmpeg...")
        urllib.request.urlretrieve(url, zip_path)
        print("下載完成，正在解壓...")
        
        # 解壓縮檔案
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall('ffmpeg_bin')
        
        # 找到解壓後的 ffmpeg.exe 路徑
        extracted_dir = None
        for item in os.listdir('ffmpeg_bin'):
            if os.path.isdir(os.path.join('ffmpeg_bin', item)) and "ffmpeg" in item.lower():
                extracted_dir = os.path.join('ffmpeg_bin', item)
                break
        
        if extracted_dir:
            # 移動 ffmpeg.exe 和 ffprobe.exe 到 ffmpeg_bin 根目錄
            bin_dir = os.path.join(extracted_dir, "bin")
            if os.path.exists(bin_dir):
                for file in os.listdir(bin_dir):
                    if file.lower() in ["ffmpeg.exe", "ffprobe.exe"]:
                        src = os.path.join(bin_dir, file)
                        dst = os.path.join('ffmpeg_bin', file)
                        shutil.copy2(src, dst)
                        print(f"已複製 {file} 到 ffmpeg_bin 目錄")
            
            # 清理解壓目錄
            shutil.rmtree(extracted_dir)
        
        # 刪除 zip 檔
        if os.path.exists(zip_path):
            os.remove(zip_path)
        
        print("FFmpeg 設置完成")
        
    except Exception as e:
        print(f"下載 FFmpeg 失敗: {str(e)}")

# 下載 FFmpeg
download_ffmpeg()

# 設置環境變數禁用 yt-dlp 更新
os.environ["YTDLP_NO_UPDATE"] = "1"

# 添加調試信息
print("開始打包程序...")
print(f"當前工作目錄: {os.getcwd()}")
print(f"Python 版本: {sys.version}")

# 構建參數列表
args = [
    'start_downloader_fixed.py',
    '--name=YouTube下載器v1.45',
    '--windowed',
    '--add-data=VERSION;.',
    '--add-data=ffmpeg_bin;ffmpeg_bin',
    '--add-data=src;src',
    '--add-data=user_preferences.json;.',
    '--hidden-import=PySide6.QtCore',
    '--hidden-import=PySide6.QtWidgets',
    '--hidden-import=PySide6.QtGui',
    '--hidden-import=PySide6.QtNetwork',
    '--hidden-import=yt_dlp',
    '--hidden-import=yt_dlp.extractor',
    '--hidden-import=yt_dlp.downloader',
    '--hidden-import=yt_dlp.postprocessor',
    '--hidden-import=yt_dlp.utils',
    '--hidden-import=urllib3',
    '--hidden-import=ssl',
    '--hidden-import=certifi',
    '--hidden-import=requests',
    '--exclude-module=PyQt6',
    '--exclude-module=PyQt5',
    '--exclude-module=tkinter',
    '--exclude-module=matplotlib',
    '--exclude-module=pandas',
    '--exclude-module=numpy',
    '--noconfirm',
    '--clean',
    '--log-level=INFO'
]

# 添加圖標（如果存在）
if os.path.exists('favicon.ico'):
    args.append('--icon=favicon.ico')

# 運行 PyInstaller
print("執行 PyInstaller 打包...")
print(f"參數: {args}")
PyInstaller.__main__.run(args)

print("打包完成！")
print(f"輸出目錄: {os.path.join(os.getcwd(), 'dist', 'YouTube下載器v1.45')}")

# 添加額外的檔案到輸出目錄
output_dir = os.path.join(os.getcwd(), 'dist', 'YouTube下載器v1.45')
print(f"正在複製額外檔案到輸出目錄: {output_dir}")

# 確保 FFmpeg 在輸出目錄中
ffmpeg_src = os.path.join('ffmpeg_bin', 'ffmpeg.exe')
ffmpeg_dst = os.path.join(output_dir, 'ffmpeg_bin', 'ffmpeg.exe')
ffprobe_src = os.path.join('ffmpeg_bin', 'ffprobe.exe')
ffprobe_dst = os.path.join(output_dir, 'ffmpeg_bin', 'ffprobe.exe')

if os.path.exists(ffmpeg_src):
    os.makedirs(os.path.dirname(ffmpeg_dst), exist_ok=True)
    shutil.copy2(ffmpeg_src, ffmpeg_dst)
    print(f"已複製 ffmpeg.exe 到輸出目錄")

if os.path.exists(ffprobe_src):
    os.makedirs(os.path.dirname(ffprobe_dst), exist_ok=True)
    shutil.copy2(ffprobe_src, ffprobe_dst)
    print(f"已複製 ffprobe.exe 到輸出目錄")

# 複製 README 文件
if os.path.exists('README.md'):
    shutil.copy('README.md', os.path.join(output_dir, 'README.md'))
    print("已複製 README.md")

# 複製使用說明
if os.path.exists('使用說明.md'):
    shutil.copy('使用說明.md', os.path.join(output_dir, '使用說明.md'))
    print("已複製使用說明.md")

# 創建啟動腳本
with open(os.path.join(output_dir, '啟動下載器.bat'), 'w', encoding='utf-8') as f:
    f.write('@echo off\n')
    f.write('echo 正在啟動 YouTube 下載器 v1.45...\n')
    f.write('start "" "YouTube下載器v1.45.exe"\n')
print("已創建啟動腳本")

print("所有檔案已複製完成！") 