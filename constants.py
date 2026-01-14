#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常數定義
UI 固定字串、顏色、提示語
"""

# 應用程式資訊
APP_TITLE = "YouTube 下載器"
APP_VERSION = "2.6.0"

# 視窗設定
WINDOW_SIZE = (500, 400)
MIN_WINDOW_SIZE = (450, 350)

# 字體設定
DEFAULT_FONT_SIZE = 12
MIN_FONT_SIZE = 8
MAX_FONT_SIZE = 20

# 主題色彩定義
THEMES = {
    'Soft Indigo': {
        'success': '#43A047',
        'error': '#E53935',
        'warning': '#FB8C00',
        'info': '#1E88E5',
        'primary': '#3949AB',
        'secondary': '#757575',
        'bg_main': '#F5F7FA',
        'bg_card': '#FFFFFF',
        'text_main': '#2C3E50',
        'accent': '#5C6BC0'
    },
    'Classic Blue': {
        'success': '#28A745',
        'error': '#DC3545',
        'warning': '#FFC107',
        'info': '#17A2B8',
        'primary': '#003366',
        'secondary': '#6C757D',
        'bg_main': '#F0F2F5',
        'bg_card': '#FFFFFF',
        'text_main': '#333333',
        'accent': '#0056B3'
    },
    'Carbon Grey': {
        'success': '#66BB6A',
        'error': '#EF5350',
        'warning': '#FFA726',
        'info': '#42A5F5',
        'primary': '#424242',
        'secondary': '#9E9E9E',
        'bg_main': '#EEEEEE',
        'bg_card': '#FFFFFF',
        'text_main': '#212121',
        'accent': '#616161'
    }
}

# 預設主題
DEFAULT_THEME = 'Soft Indigo'

# 指向當前有效色彩 (相容性保留，初始化時會被 main.py 覆蓋)
COLORS = THEMES[DEFAULT_THEME]

# UI 文字
UI_TEXT = {
    'url_placeholder': '請輸入視頻網址（支援 YouTube、Bilibili、TikTok 等）',
    'download_path_label': '下載路徑：',
    'browse_button': '瀏覽...',
    'download_button': '開始下載',
    'pause_button': '暫停',
    'resume_button': '繼續',
    'cancel_button': '取消',
    'copy_url_button': '複製網址',
    'open_browser_button': '瀏覽器開啟',
    'clear_button': '清空',
    'retry_button': '重試',
    'show_log_button': '顯示日誌',
    'hide_log_button': '隱藏日誌',
}

# 狀態訊息
STATUS_MESSAGES = {
    'ready': '就緒',
    'downloading': '下載中...',
    'paused': '已暫停',
    'completed': '下載完成',
    'failed': '下載失敗',
    'cancelled': '已取消',
    'extracting_info': '正在解析視頻資訊...',
    'merging': '正在合併音視頻...',
}

# 錯誤訊息
ERROR_MESSAGES = {
    'invalid_url': '請輸入有效的視頻網址',
    'no_download_path': '請選擇下載路徑',
    'download_failed': '下載失敗，請檢查網路連接或重試',
    'ffmpeg_not_found': '未找到 FFmpeg，某些功能可能無法使用',
    'permission_denied': '權限不足，無法寫入指定路徑',
    'disk_space_low': '磁碟空間不足',
    'network_error': '網路連接錯誤',
}

# 成功訊息
SUCCESS_MESSAGES = {
    'download_complete': '下載完成！',
    'url_copied': '網址已複製到剪貼板',
    'settings_saved': '設定已保存',
}

# 支援的平台
SUPPORTED_PLATFORMS = {
    'youtube.com': 'YouTube',
    'youtu.be': 'YouTube',
    'bilibili.com': 'Bilibili',
    'b23.tv': 'Bilibili',
    'tiktok.com': 'TikTok',
    'douyin.com': '抖音',
    'instagram.com': 'Instagram',
    'facebook.com': 'Facebook',
    'twitter.com': 'X (Twitter)',
    'x.com': 'X (Twitter)',
    'weibo.com': '微博',
    'kuaishou.com': '快手',
}

# 外部下載器連結
EXTERNAL_DOWNLOADERS = {
    'savefrom': {
        'name': 'SaveFrom.net',
        'url': 'https://savefrom.net/',
        'description': '支援多平台的線上下載工具'
    },
    'y2mate': {
        'name': 'Y2mate',
        'url': 'https://y2mate.com/',
        'description': 'YouTube 視頻下載器'
    },
    'snaptube': {
        'name': 'SnapTube',
        'url': 'https://snaptube.com/',
        'description': '多平台視頻下載工具'
    }
}

# 檔案格式
VIDEO_FORMATS = ['mp4', 'webm', 'mkv', 'avi', 'mov']
AUDIO_FORMATS = ['mp3', 'aac', 'ogg', 'wav', 'm4a']

# 畫質選項
QUALITY_OPTIONS = [
    ('最佳畫質', 'best'),
    ('1080p', '1080p'),
    ('720p', '720p'),
    ('480p', '480p'),
    ('360p', '360p'),
    ('僅音頻', 'audio')
]

# 日誌設定
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
LOG_FILE = 'logs/app.log'
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 常量路徑處理
import os
import sys

if getattr(sys, 'frozen', False):
    # 打包後的環境 (EXE 所在目錄)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 開發環境 (程式進入點所在目錄)
    # 使用當前執行路徑或 __main__ 所在目錄，避免被 nested libs 誤導
    import __main__
    if hasattr(__main__, '__file__'):
        BASE_DIR = os.path.dirname(os.path.abspath(__main__.__file__))
    else:
        BASE_DIR = os.getcwd()

# 設定檔案路徑
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
DATA_DIR = os.path.join(BASE_DIR, 'data')
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

SETTINGS_FILE = os.path.join(CONFIG_DIR, 'settings.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')

# 下載設定
DEFAULT_DOWNLOAD_PATH = 'downloads'
MAX_CONCURRENT_DOWNLOADS = 3
DOWNLOAD_TIMEOUT = 300  # 5分鐘
RETRY_ATTEMPTS = 3

# 進度更新間隔（秒）
PROGRESS_UPDATE_INTERVAL = 0.5

# 檔名前綴選項來源設定
import os
import shutil
from utils.path_utils import get_resource_path

# 內建預設（用於初始化檔案與後備）
_DEFAULT_FILENAME_PREFIXES = [
    '',
    'per- ',
    'per best- ',
    'per best2- ',
    'per best3- ',
    'per nice- ',
]

PRENAME_FILE = f'{CONFIG_DIR}/prename.txt'

def _load_filename_prefixes():
    """從 config/prename.txt 讀取前綴清單；若檔案不存在則用內建預設建立。
    - 忽略以 # 開頭的註解行
    - 忽略空白行
    - 永遠確保空字串 '' 作為「無前綴」選項出現在第一個
    """
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)

        # 初始化檔案（若不存在）：
        # 1) 優先從打包內建資源（config/prename.txt）複製到外部 config 目錄
        # 2) 若內建資源不存在，再用程式內建預設生成
        if not os.path.exists(PRENAME_FILE):
            bundled = get_resource_path('config/prename.txt')
            try:
                if os.path.exists(bundled):
                    shutil.copyfile(bundled, PRENAME_FILE)
                else:
                    with open(PRENAME_FILE, 'w', encoding='utf-8') as f:
                        f.write('# 檔名前綴清單，一行一個；使用者可自由編輯\n')
                        f.write('# 以 # 開頭為註解，空白行將被忽略\n')
                        for item in _DEFAULT_FILENAME_PREFIXES:
                            if item:  # 不將空字串寫入檔案，由程式保留為第一個選項
                                f.write(item + '\n')
            except Exception:
                # 若複製/生成失敗，忽略，稍後使用內建預設作為後備
                pass

        # 讀取檔案
        prefixes = []
        with open(PRENAME_FILE, 'r', encoding='utf-8') as f:
            for raw_line in f:
                line = raw_line.strip('\r\n')
                if not line or line.lstrip().startswith('#'):
                    continue
                prefixes.append(line.strip())

        # 確保空字串作為第一個選項
        return [''] + prefixes
    except Exception:
        # 若發生任何錯誤，回退到內建預設
        return _DEFAULT_FILENAME_PREFIXES[:]

# 實際使用的檔名前綴清單
FILENAME_PREFIXES = _load_filename_prefixes()

def reload_filename_prefixes():
    """重新載入 prename.txt 並更新全域 FILENAME_PREFIXES。"""
    global FILENAME_PREFIXES
    FILENAME_PREFIXES = _load_filename_prefixes()
    return FILENAME_PREFIXES

def get_filename_prefixes():
    """取得目前的檔名前綴清單（供外部讀取）。"""
    return FILENAME_PREFIXES