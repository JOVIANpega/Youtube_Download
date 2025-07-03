#!/usr/bin/env python3
"""
YouTube 下載器測試腳本
Test script for YouTube downloader
YouTubeダウンローダーテストスクリプト
유튜브 다운로더 테스트 스크립트
"""

import yt_dlp
import os

def test_yt_dlp():
    """測試 yt-dlp 基本功能"""
    print("測試 yt-dlp 功能...")
    
    # 測試 URL (一個公開的 YouTube 影片)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        # 設定下載選項
        ydl_opts = {
            'outtmpl': 'test_%(title)s.%(ext)s',
            'format': 'best[filesize<10M]',  # 限制檔案大小小於 10MB
            'quiet': True,
        }
        
        print("正在獲取影片資訊...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 先獲取資訊
            info = ydl.extract_info(test_url, download=False)
            print(f"✓ 成功獲取影片資訊")
            print(f"  標題: {info.get('title', 'N/A')}")
            print(f"  時長: {info.get('duration', 'N/A')} 秒")
            print(f"  上傳者: {info.get('uploader', 'N/A')}")
            
            # 測試下載 (只下載前 10 秒)
            print("\n正在測試下載 (僅前 10 秒)...")
            ydl_opts['external_downloader'] = 'ffmpeg'
            ydl_opts['external_downloader_args'] = ['-t', '10']  # 只下載前 10 秒
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([test_url])
            
            print("✓ 測試下載完成")
            
            # 清理測試檔案
            for file in os.listdir('.'):
                if file.startswith('test_'):
                    os.remove(file)
                    print(f"  已清理測試檔案: {file}")
            
    except Exception as e:
        print(f"✗ 測試失敗: {e}")
        return False
    
    print("\n🎉 所有測試通過！yt-dlp 功能正常")
    return True

def test_ffmpeg():
    """測試 FFmpeg 是否可用"""
    print("\n測試 FFmpeg...")
    
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ FFmpeg 可用")
            return True
        else:
            print("✗ FFmpeg 不可用")
            return False
    except Exception as e:
        print(f"✗ FFmpeg 測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("YouTube 下載器功能測試")
    print("=" * 50)
    
    # 測試 FFmpeg
    ffmpeg_ok = test_ffmpeg()
    
    # 測試 yt-dlp
    ytdlp_ok = test_yt_dlp()
    
    print("\n" + "=" * 50)
    if ffmpeg_ok and ytdlp_ok:
        print("🎉 所有組件都正常工作！")
        print("你可以開始使用 YouTube 下載器了。")
    else:
        print("⚠️  部分組件有問題，請檢查安裝。")
        
    print("\n使用方法:")
    print("python src/main.py") 