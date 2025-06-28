#!/usr/bin/env python3
"""
測試影片標題獲取
Test Video Title Extraction
動画タイトル取得テスト
동영상 제목 추출 테스트
"""

import ssl
import os
import yt_dlp

# 修復 SSL 問題
def fix_ssl_issues():
    """修復 SSL 證書問題"""
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl._create_default_https_context = lambda: ssl_context
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        print("✓ SSL 問題已修復")
        return True
    except Exception as e:
        print(f"✗ SSL 修復失敗: {e}")
        return False

def test_title_extraction():
    """測試標題獲取"""
    url = "https://www.youtube.com/watch?v=wa3f6E1qf-Y"
    expected_title = "Podezřelý zloděj nebo vandal u zaparkovaného auta | Policie v akci"
    
    print("測試影片標題獲取")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"預期標題: {expected_title}")
    print()
    
    # 方法 1: 基本方法
    print("方法 1: 基本方法")
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Video')
            print(f"獲取到的標題: {title}")
            print(f"是否匹配: {'✓' if title == expected_title else '✗'}")
    except Exception as e:
        print(f"✗ 失敗: {e}")
    
    print()
    
    # 方法 2: 強化方法
    print("方法 2: 強化方法")
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'socket_timeout': 60,
            'retries': 5,
            'fragment_retries': 5,
            'extractor_retries': 5,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Video')
            print(f"獲取到的標題: {title}")
            print(f"是否匹配: {'✓' if title == expected_title else '✗'}")
    except Exception as e:
        print(f"✗ 失敗: {e}")
    
    print()
    
    # 方法 3: 備用方法
    print("方法 3: 備用方法")
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'format': 'worst',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown Video')
            print(f"獲取到的標題: {title}")
            print(f"是否匹配: {'✓' if title == expected_title else '✗'}")
    except Exception as e:
        print(f"✗ 失敗: {e}")

def test_multiple_urls():
    """測試多個 URL"""
    urls = [
        "https://www.youtube.com/watch?v=wa3f6E1qf-Y",
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://www.youtube.com/watch?v=jNQXAC9IVRw"
    ]
    
    print("\n測試多個 URL")
    print("=" * 50)
    
    for url in urls:
        print(f"\n測試 URL: {url}")
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'ignoreerrors': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown Video')
                print(f"標題: {title}")
        except Exception as e:
            print(f"✗ 失敗: {e}")

if __name__ == "__main__":
    # 修復 SSL 問題
    fix_ssl_issues()
    
    # 測試標題獲取
    test_title_extraction()
    
    # 測試多個 URL
    test_multiple_urls() 