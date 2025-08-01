#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
平台識別模組 v2.0 - 由 Augment AI 開發
基於yt-dlp支援的數千個網站進行擴展
支援更多平台和更智能的檢測
"""

import re
from logger import logger

# yt-dlp支援的主要平台列表
SUPPORTED_PLATFORMS = {
    # 主流影片平台
    'youtube.com': {'name': 'YouTube', 'quality': '8K', 'icon': '▶️'},
    'youtu.be': {'name': 'YouTube', 'quality': '8K', 'icon': '▶️'},
    'bilibili.com': {'name': 'Bilibili', 'quality': '4K', 'icon': '📺'},
    'b23.tv': {'name': 'Bilibili', 'quality': '4K', 'icon': '📺'},
    
    # 社交媒體
    'tiktok.com': {'name': 'TikTok', 'quality': '1080P', 'icon': '🎵'},
    'vm.tiktok.com': {'name': 'TikTok', 'quality': '1080P', 'icon': '🎵'},
    'instagram.com': {'name': 'Instagram', 'quality': '1080P', 'icon': '📷'},
    'facebook.com': {'name': 'Facebook', 'quality': '1080P', 'icon': '📘'},
    'fb.watch': {'name': 'Facebook', 'quality': '1080P', 'icon': '📘'},
    'twitter.com': {'name': 'Twitter/X', 'quality': '1080P', 'icon': '🐦'},
    'x.com': {'name': 'Twitter/X', 'quality': '1080P', 'icon': '🐦'},
    'threads.net': {'name': 'Threads', 'quality': '720P', 'icon': '🧵'},
    
    # 中國平台
    'v.qq.com': {'name': 'QQ影片', 'quality': '4K', 'icon': '🐧'},
    'iqiyi.com': {'name': '愛奇藝', 'quality': '4K', 'icon': '🎬'},
    'youku.com': {'name': '優酷', 'quality': '1080P', 'icon': '📹'},
    'douyin.com': {'name': '抖音', 'quality': '1080P', 'icon': '🎵'},
    
    # 國際平台
    'vimeo.com': {'name': 'Vimeo', 'quality': '4K', 'icon': '🎥'},
    'dailymotion.com': {'name': 'Dailymotion', 'quality': '1080P', 'icon': '📺'},
    'twitch.tv': {'name': 'Twitch', 'quality': '1080P', 'icon': '🎮'},
    'reddit.com': {'name': 'Reddit', 'quality': '1080P', 'icon': '🤖'},
    
    # 音頻平台
    'soundcloud.com': {'name': 'SoundCloud', 'quality': 'Audio', 'icon': '🎧'},
    'mixcloud.com': {'name': 'Mixcloud', 'quality': 'Audio', 'icon': '🎧'},
    
    # 教育平台
    'ted.com': {'name': 'TED', 'quality': '1080P', 'icon': '🎓'},
    'coursera.org': {'name': 'Coursera', 'quality': '720P', 'icon': '📚'},
    'udemy.com': {'name': 'Udemy', 'quality': '720P', 'icon': '📚'},
    
    # 新聞平台
    'cnn.com': {'name': 'CNN', 'quality': '1080P', 'icon': '📰'},
    'bbc.co.uk': {'name': 'BBC', 'quality': '1080P', 'icon': '📰'},
    'reuters.com': {'name': 'Reuters', 'quality': '720P', 'icon': '📰'},
}

def identify_platform(url):
    """
    識別影片平台 - v2.0 擴展版本
    基於yt-dlp支援的數千個網站
    
    Args:
        url (str): 影片網址
        
    Returns:
        dict: 包含平台資訊的字典
    """
    if not url or not isinstance(url, str):
        return get_unknown_platform()
    
    url_lower = url.strip().lower()
    
    # 檢查已知平台
    for domain, info in SUPPORTED_PLATFORMS.items():
        if domain in url_lower:
            logger.info(f"檢測到 {info['name']} 連結: {url}")
            return {
                'name': info['name'],
                'supported': True,
                'quality': info['quality'],
                'icon': info['icon'],
                'notes': f"yt-dlp完全支援，最高{info['quality']}品質",
                'download_options': get_download_options(info['name'])
            }
    
    # 特殊處理一些需要額外檢查的平台
    special_platforms = check_special_platforms(url_lower)
    if special_platforms:
        return special_platforms
    
    # 未知平台但yt-dlp可能支援
    logger.info(f"未知平台，嘗試使用yt-dlp: {url}")
    return {
        'name': '未知平台',
        'supported': True,
        'quality': '720P+',
        'icon': '🌐',
        'notes': 'yt-dlp支援1000+網站，值得嘗試',
        'download_options': get_download_options('generic')
    }

def check_special_platforms(url_lower):
    """檢查需要特殊處理的平台"""
    
    # 成人平台（如果需要的話）
    adult_domains = ['pornhub.com', 'xvideos.com', 'xhamster.com']
    for domain in adult_domains:
        if domain in url_lower:
            return {
                'name': domain.split('.')[0].title(),
                'supported': True,
                'quality': '1080P',
                'icon': '🔞',
                'notes': 'yt-dlp支援，請確保符合當地法律',
                'download_options': get_download_options('adult')
            }
    
    # 直播平台
    live_domains = ['live.', 'stream.', 'broadcast.']
    if any(live in url_lower for live in live_domains):
        return {
            'name': '直播平台',
            'supported': True,
            'quality': '1080P',
            'icon': '📡',
            'notes': '可能支援直播下載，取決於平台',
            'download_options': get_download_options('live')
        }
    
    return None

def get_download_options(platform_name):
    """根據平台獲取最佳下載選項"""
    
    options = {
        'YouTube': {
            'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            'prefer_mp4': True,
            'merge_output_format': 'mp4'
        },
        'Bilibili': {
            'format': 'bestvideo+bestaudio/best',
            'prefer_mp4': True
        },
        'TikTok': {
            'format': 'best',
            'no_watermark': True
        },
        'Instagram': {
            'format': 'best[height<=1080]',
            'prefer_mp4': True
        },
        'Facebook': {
            'format': 'best[height<=720][ext=mp4]/best[ext=mp4]/best',
            'prefer_mp4': True
        },
        'Twitter/X': {
            'format': 'best[height<=1080]',
            'prefer_mp4': True
        },
        'adult': {
            'format': 'best[height<=1080]',
            'prefer_mp4': True,
            'age_limit': 18
        },
        'live': {
            'format': 'best',
            'live_from_start': True
        },
        'generic': {
            'format': 'best[height<=720]',
            'prefer_mp4': True
        }
    }
    
    return options.get(platform_name, options['generic'])

def get_unknown_platform():
    """返回未知平台的預設資訊"""
    return {
        'name': '未知平台',
        'supported': False,
        'quality': 'N/A',
        'icon': '❓',
        'notes': '無法識別的URL格式',
        'download_options': {}
    }

def get_platform_stats():
    """獲取支援平台統計"""
    return {
        'total_platforms': len(SUPPORTED_PLATFORMS),
        'video_platforms': len([p for p in SUPPORTED_PLATFORMS.values() if p['quality'] != 'Audio']),
        'audio_platforms': len([p for p in SUPPORTED_PLATFORMS.values() if p['quality'] == 'Audio']),
        'max_quality': '8K',
        'yt_dlp_supported': '1000+'
    }

def is_supported_url(url):
    """快速檢查URL是否被支援"""
    if not url:
        return False
    
    url_lower = url.strip().lower()
    return any(domain in url_lower for domain in SUPPORTED_PLATFORMS.keys())

# 向後兼容性
def get_platform_info(url):
    """向後兼容的函數名稱"""
    return identify_platform(url)
