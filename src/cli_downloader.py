#!/usr/bin/env python3
"""
YouTube 下載器命令行版本
Command Line YouTube Downloader
YouTubeダウンローダーコマンドライン版
유튜브 다운로더 명령줄 버전
"""

import yt_dlp
import os
import sys
import argparse
from pathlib import Path

def download_video(url, output_path, format_choice, quiet=False):
    """下載 YouTube 影片"""
    
    # 設定下載選項
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'quiet': quiet,
        'no_warnings': quiet,
    }
    
    # 根據格式選擇設定
    if format_choice == "最高品質影片":
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
    elif format_choice == "僅音訊 (MP3)":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif format_choice == "僅音訊 (WAV)":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
        }]
    else:  # 預設品質
        ydl_opts['format'] = 'best'
    
    try:
        print(f"開始下載: {url}")
        print(f"格式: {format_choice}")
        print(f"下載路徑: {output_path}")
        print("-" * 50)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 先獲取資訊
            if not quiet:
                print("獲取影片資訊...")
            info = ydl.extract_info(url, download=False)
            
            if not quiet:
                print(f"標題: {info.get('title', 'N/A')}")
                print(f"時長: {info.get('duration', 'N/A')} 秒")
                print(f"上傳者: {info.get('uploader', 'N/A')}")
                print("開始下載...")
            
            # 下載
            ydl.download([url])
        
        print("✓ 下載完成！")
        return True
        
    except Exception as e:
        print(f"✗ 下載失敗: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="YouTube 影片下載器命令行版本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  python cli_downloader.py "https://www.youtube.com/watch?v=VIDEO_ID"
  python cli_downloader.py "URL" --format "僅音訊 (MP3)" --output "C:\\Downloads"
  python cli_downloader.py "URL" --format "最高品質影片" --quiet
        """
    )
    
    parser.add_argument('url', help='YouTube 影片 URL')
    parser.add_argument(
        '--format', '-f',
        choices=['預設品質', '最高品質影片', '僅音訊 (MP3)', '僅音訊 (WAV)'],
        default='預設品質',
        help='下載格式 (預設: 預設品質)'
    )
    parser.add_argument(
        '--output', '-o',
        default=os.path.expanduser("~/Downloads"),
        help='下載路徑 (預設: ~/Downloads)'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='安靜模式，不顯示詳細資訊'
    )
    
    args = parser.parse_args()
    
    # 檢查 URL
    if not args.url.startswith('http'):
        print("錯誤: 請提供有效的 URL")
        sys.exit(1)
    
    # 檢查輸出路徑
    output_path = Path(args.output)
    if not output_path.exists():
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"錯誤: 無法創建輸出目錄: {e}")
            sys.exit(1)
    
    # 顯示語言選擇
    if not args.quiet:
        print("YouTube 下載器命令行版本")
        print("YouTube Video Downloader CLI")
        print("YouTube動画ダウンローダーCLI")
        print("유튜브 비디오 다운로더 CLI")
        print("=" * 50)
    
    # 下載
    success = download_video(args.url, str(output_path), args.format, args.quiet)
    
    if success:
        print("🎉 下載成功完成！")
        sys.exit(0)
    else:
        print("❌ 下載失敗")
        sys.exit(1)

if __name__ == "__main__":
    main() 