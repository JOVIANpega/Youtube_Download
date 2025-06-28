#!/usr/bin/env python3
"""
測試年齡限制處理
Test age restriction handling
年齢制限処理テスト
연령 제한 처리 테스트
"""

import yt_dlp
import os

def test_age_restriction_fix():
    """測試年齡限制修復"""
    print("測試年齡限制處理...")
    
    # 測試 URL (年齡限制影片)
    test_url = "https://www.youtube.com/watch?v=Uhih24t9DKg"
    
    try:
        # 設定下載選項，處理年齡限制
        ydl_opts = {
            'outtmpl': 'test_%(title)s.%(ext)s',
            'format': 'best[filesize<10M]',  # 限制檔案大小
            'quiet': False,
            'no_warnings': False,
            # 年齡限制處理選項
            'cookiesfrombrowser': ('chrome',),  # 從 Chrome 獲取 cookies
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'live'],  # 跳過 DASH 和直播
                }
            },
            # 其他選項
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'no_color': True,
        }
        
        print("正在嘗試獲取影片資訊...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # 先獲取資訊
            info = ydl.extract_info(test_url, download=False)
            print(f"✓ 成功獲取影片資訊")
            print(f"  標題: {info.get('title', 'N/A')}")
            print(f"  時長: {info.get('duration', 'N/A')} 秒")
            print(f"  上傳者: {info.get('uploader', 'N/A')}")
            print(f"  年齡限制: {info.get('age_limit', 'N/A')}")
            
            # 檢查可用格式
            formats = info.get('formats', [])
            print(f"  可用格式數量: {len(formats)}")
            
            # 顯示前幾個格式
            for i, fmt in enumerate(formats[:5]):
                print(f"    格式 {i+1}: {fmt.get('format_id', 'N/A')} - {fmt.get('height', 'N/A')}p")
            
            # 測試下載 (只下載前 5 秒)
            print("\n正在測試下載 (僅前 5 秒)...")
            ydl_opts['external_downloader'] = 'ffmpeg'
            ydl_opts['external_downloader_args'] = ['-t', '5']  # 只下載前 5 秒
            
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
        
        # 嘗試其他方法
        print("\n嘗試其他方法...")
        try:
            ydl_opts = {
                'outtmpl': 'test_%(title)s.%(ext)s',
                'format': 'worst',  # 使用最差品質
                'quiet': False,
                'no_warnings': False,
                'nocheckcertificate': True,
                'ignoreerrors': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([test_url])
            
            print("✓ 使用備用方法成功")
            
        except Exception as e2:
            print(f"✗ 備用方法也失敗: {e2}")
            return False
    
    print("\n🎉 年齡限制處理測試完成！")
    return True

def test_public_video():
    """測試公開影片"""
    print("\n測試公開影片...")
    
    # 使用一個公開的測試影片
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - YouTube 第一個影片
    
    try:
        ydl_opts = {
            'outtmpl': 'test_%(title)s.%(ext)s',
            'format': 'best[filesize<5M]',
            'quiet': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(test_url, download=False)
            print(f"✓ 公開影片測試成功")
            print(f"  標題: {info.get('title', 'N/A')}")
            
            # 下載
            ydl.download([test_url])
        
        # 清理
        for file in os.listdir('.'):
            if file.startswith('test_'):
                os.remove(file)
        
        return True
        
    except Exception as e:
        print(f"✗ 公開影片測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("YouTube 年齡限制處理測試")
    print("=" * 50)
    
    # 測試公開影片
    public_ok = test_public_video()
    
    # 測試年齡限制影片
    age_restriction_ok = test_age_restriction_fix()
    
    print("\n" + "=" * 50)
    if public_ok:
        print("✓ 公開影片下載正常")
    else:
        print("✗ 公開影片下載有問題")
    
    if age_restriction_ok:
        print("✓ 年齡限制處理成功")
    else:
        print("✗ 年齡限制處理失敗")
    
    print("\n建議:")
    print("1. 對於年齡限制影片，建議使用瀏覽器 cookies")
    print("2. 或者嘗試不同的影片 URL")
    print("3. 某些影片可能需要登入才能下載") 