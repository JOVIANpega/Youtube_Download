# YouTube 下載器

一個功能完整的多平台視頻下載器，支援 YouTube、Bilibili、TikTok 等多個平台。

## 功能特色

- **多平台支援**: YouTube、Bilibili、TikTok、Instagram、Facebook、X(Twitter)、微博、快手等
- **高品質下載**: 優先最高畫質，保底 720p
- **智能合併**: 自動合併音視頻軌道
- **友好介面**: 簡潔的 GUI 介面，支援字體縮放
- **歷史記錄**: 完整的下載歷史管理
- **外部工具**: 內建外部下載器連結
- **進度追蹤**: 多行文字即時顯示檔案名、進度百分比和速度
- **多執行緒下載**: 背景處理，GUI 不凍結，支援長時間下載
- **自動依賴安裝**: 檢測並自動安裝所需依賴（如 yt-dlp）
- **便捷檔案管理**: 一鍵開啟下載資料夾
- **完成提醒**: 下載完成後詢問是否播放影片
- **檔名前綴**: 支援 custom 檔名前綴（per-, per best-, per best2-, per best3-, per nice-）
- **詳細狀態顯示**: ScrolledText 多行狀態區域，支援歷史記錄查看

## 技術架構

- **GUI框架**: Tkinter + ttk
- **下載引擎**: yt-dlp
- **音視頻處理**: FFmpeg
- **多執行緒**: 背景執行緒下載，不阻塞 UI
- **跨平台支援**: Windows、macOS、Linux 檔案系統操作
- **智能格式選擇**: 自動選擇最佳音視頻格式組合
- **資料存儲**: JSON 格式設定和歷史記錄
- **日誌系統**: 完整的日誌記錄和顯示

## 安裝需求

```bash
pip install -r requirements.txt
```

### 必要依賴

- Python 3.7+
- yt-dlp
- requests
- Pillow (可選，用於圖標)

### 可選依賴

- FFmpeg (用於音視頻合併)

## 使用方法

### 快速開始

1. **一鍵啟動**（推薦）：
```bash
python start.py
```
這個腳本會自動檢查環境、安裝依賴並選擇最佳啟動方式。

2. **手動啟動**：
```bash
# 檢查依賴
python check_dependencies.py

# 安裝依賴（如需要）
python install_deps.py

# 運行測試
python run_tests.py

# 啟動完整版
python main.py

# 或啟動簡化版
python simple_main.py
```

### 基本使用

1. 在「下載」頁面輸入視頻網址
2. 選擇下載路徑和品質
3. 點擊「開始下載」

### 進階功能

- **字體調整**: 使用右上角的 A-/A+ 按鈕調整界面字體大小
- **開啟資料夾**: 下載路徑旁「開啟資料夾」按鈕可直接瀏覽下載位置
- **進度顯示**: 多行文字顯示檔案名、即時進度百分比和下載速度
- **自動安裝**: 缺少依賴時會詢問並自動安裝（如 yt-dlp）
- **播放詢問**: 下載完成後彈出視窗詢問是否立即播放
- **進階選項**: 點擊「進階選項」設定字幕、格式等
- **歷史管理**: 在「歷史記錄」頁面查看和管理下載記錄
- **外部工具**: 在「外部下載器」頁面使用線上下載工具

## 檔案結構

```
├── main.py                 # 主程式入口
├── constants.py           # 常數定義
├── version_info.py        # 版本資訊
├── logging_config.py      # 日誌配置
├── requirements.txt       # 依賴清單
├── ui_download.py         # 下載頁面
├── ui_external.py         # 外部下載器頁面
├── ui_history.py          # 歷史記錄頁面
├── utils/                 # 工具模組
│   ├── path_utils.py      # 路徑處理
│   ├── ui_fonts.py        # 字體管理
│   ├── validators.py      # 驗證工具
│   ├── naming.py          # 檔名處理
│   └── threading_utils.py # 執行緒工具
├── services/              # 服務模組
│   ├── downloader.py      # 下載器服務
│   ├── ffmpeg_manager.py  # FFmpeg 管理
│   ├── history_store.py   # 歷史記錄存儲
│   └── settings.py        # 設定管理
├── models/                # 資料模型
│   └── types.py           # 類型定義
├── assets/                # 資源檔案
├── config/                # 配置檔案
├── data/                  # 資料檔案
├── logs/                  # 日誌檔案
└── downloads/             # 預設下載目錄
```

## 測試

運行測試腳本檢查功能：

```bash
python test_app.py
```

## 打包發布

### 方法一：使用提供的 BAT 檔案（推薦）
```bash
# 運行打包腳本
build_exe.bat
```

### 方法二：手動打包
```bash
# 安裝 PyInstaller
pip install pyinstaller

# 打包為單一檔案（無控制台視窗）
pyinstaller --onefile --noconsole --icon=assets/icon.ico main.py

# 打包為單一檔案（附控制台除錯）
pyinstaller --onefile --console --icon=assets/icon.ico main.py
```

打包後的檔案位於 `dist/` 資料夾中。

## 支援的平台

- YouTube (youtube.com, youtu.be)
- Bilibili (bilibili.com, b23.tv)
- TikTok (tiktok.com)
- 抖音 (douyin.com)
- Instagram (instagram.com)
- Facebook (facebook.com)
- X/Twitter (twitter.com, x.com)
- 微博 (weibo.com)
- 快手 (kuaishou.com)

## 使用提示

### 首次使用
- 程式會自動檢測並安裝所需依賴（如 yt-dlp）
- 安裝過程可能需要數分鐘，請耐心等待
- 如遇安裝失敗，可手動運行 `pip install yt-dlp`

### 最佳體驗
- 確保網路連線穩定，避免下載中斷
- 建議選擇合適的畫質以平衡檔案大小與品質
- 下載大檔案時，建議使用 Wi-Fi 避免流量消耗

### 故障排除
- 如遇下載失敗，檢查網址是否有效
- 某些視頻可能因版權或地區限制無法下載
- 更新 yt-dlp：`pip install --upgrade yt-dlp`

## 注意事項

1. 請遵守各平台的使用條款
2. 僅供個人學習和研究使用
3. 下載的內容請勿用於商業用途
4. 建議安裝 FFmpeg 以獲得最佳體驗
5. 請注意合法使用，尊重版權

## 版本歷史

### v1.3.0 (最新)
- **多行狀態顯示**: 使用 ScrolledText 替代單行 Label，完整顯示長狀態信息
- **檔名前綴自定義**: 新增檔案命名選項（per-, per best-, per best2-, per best3-, per nice-）
- **進度回調追蹤**: 修復並強化進度回調機制，確保 GUI 顯示與實際下載同步
- **時間戳記顯示**: 狀態更新加入時間戳記，便於追蹤下載時間
- **自動滾動**: 狀態區域自動滾動到最新訊息，保持可讀性
- **格式選擇優化**: 重新設計 yt-dlp 格式選擇邏輯，支援更多視頻類型
- **除錯信息強化**: 終端輸出詳細進度信息，便於故障排除

### v1.2.0
- **多執行緒下載**: 修復 GUI 凍結問題，下載過程不阻塞界面
- **進度百分比顯示**: 在進度條旁即時顯示下載百分比
- **檔案管理增強**: 新增「開啟資料夾」按鈕，一鍵瀏覽下載位置
- **完成提醒功能**: 下載完成後自動詢問是否播放影片
- **自動依賴安裝**: 智能檢測並自動安裝缺少的依賴包
- **字體管理修復**: 解決 Tkinter 字體設定錯誤問題
- **跨平台檔案操作**: 支援 Windows、macOS、Linux 系統檔案開啟
- **智能格式選擇**: 改善 yt-dlp 格式選擇邏輯，提升下載成功率

### v1.1.0
- 修復依賴問題
- 改善字體管理
- 優化錯誤處理

### v1.0.0
- 初始版本
- 基本下載功能
- 多平台支援
- GUI 介面
- 歷史記錄
- 外部下載器整合

## 授權

本專案僅供學習和研究使用。