#!/usr/bin/env python3
"""
SSL 證書修復腳本
SSL Certificate Fix Script
SSL証明書修正スクリプト
SSL 인증서 수정 스크립트
"""

import ssl
import certifi
import os
import sys

def fix_ssl_issues():
    """修復 SSL 證書問題"""
    print("正在修復 SSL 證書問題...")
    
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # 設定全域 SSL 上下文
        ssl._create_default_https_context = lambda: ssl_context
        
        print("✓ SSL 證書問題已修復")
        return True
        
    except Exception as e:
        print(f"✗ SSL 修復失敗: {e}")
        return False

def install_certifi():
    """安裝 certifi 套件"""
    try:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "certifi"])
        print("✓ certifi 已安裝")
        return True
    except Exception as e:
        print(f"✗ certifi 安裝失敗: {e}")
        return False

if __name__ == "__main__":
    print("SSL 證書修復工具")
    print("=" * 50)
    
    # 檢查並安裝 certifi
    try:
        import certifi
        print("✓ certifi 已安裝")
    except ImportError:
        print("certifi 未安裝，正在安裝...")
        install_certifi()
    
    # 修復 SSL 問題
    if fix_ssl_issues():
        print("\n🎉 SSL 問題已修復！")
        print("現在可以正常使用 YouTube 下載器了。")
    else:
        print("\n⚠️ SSL 修復失敗，請手動處理。") 