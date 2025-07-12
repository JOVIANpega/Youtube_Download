#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
創建簡單的圖標文件
"""

import os
from PIL import Image, ImageDraw

# 確保安裝了Pillow
try:
    from PIL import Image
except ImportError:
    import subprocess
    import sys
    print("正在安裝Pillow...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

# 創建圖標
def create_icon():
    # 創建一個256x256的圖像
    img = Image.new('RGBA', (256, 256), color=(255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    
    # 繪製一個簡單的圖標 - 紅色圓形背景
    draw.ellipse((20, 20, 236, 236), fill=(220, 50, 50, 255))
    
    # 繪製白色的播放按鈕
    draw.polygon([(90, 80), (90, 176), (186, 128)], fill=(255, 255, 255, 255))
    
    # 保存為.ico文件
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # 保存為PNG
    img.save('assets/icon.png')
    
    # 轉換為ICO (需要不同尺寸)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    img.save('assets/icon.ico', sizes=icon_sizes)
    
    print("圖標已創建: assets/icon.ico")

if __name__ == "__main__":
    create_icon() 