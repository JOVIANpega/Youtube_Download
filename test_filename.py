#!/usr/bin/env python3
"""
檔案名稱處理測試
Filename Processing Test
ファイル名処理テスト
파일명 처리 테스트
"""

import re
import os

def sanitize_filename(filename):
    """清理檔案名稱，移除或替換不合法字符"""
    # 移除或替換不合法字符
    # Windows 不合法字符: < > : " | ? * \ /
    # 也移除其他可能造成問題的字符
    illegal_chars = r'[<>:"|?*\\/\n\r\t]'
    filename = re.sub(illegal_chars, '_', filename)
    
    # 移除開頭和結尾的空格和點
    filename = filename.strip(' .')
    
    # 限制檔案名稱長度 (Windows 限制為 255 字符，但我們設為 200 以留餘地)
    if len(filename) > 200:
        filename = filename[:200]
    
    # 如果檔案名稱為空，使用預設名稱
    if not filename:
        filename = "YouTube_Video"
    
    return filename

def test_filename_processing():
    """測試檔案名稱處理"""
    print("檔案名稱處理測試")
    print("=" * 50)
    
    test_cases = [
        "正常影片標題",
        "影片標題 with 特殊字符 < > : \" | ? * \\ /",
        "影片標題 with 換行符\n和製表符\t",
        "影片標題 with 點點點...",
        "  開頭和結尾有空格  ",
        "影片標題 with 表情符號 😀🎵🎬",
        "影片標題 with 數字 123 和 符號 @#$%",
        "非常長的影片標題 " * 20,  # 測試長度限制
        "",  # 空字串
        "   ",  # 只有空格
        "影片標題 with 中文、English、日本語、한국어",
    ]
    
    for i, original in enumerate(test_cases, 1):
        cleaned = sanitize_filename(original)
        print(f"測試 {i}:")
        print(f"  原始: '{original}'")
        print(f"  清理後: '{cleaned}'")
        print(f"  長度: {len(cleaned)}")
        print()
    
    print("測試完成！")

if __name__ == "__main__":
    test_filename_processing() 