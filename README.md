# YouTube 下載器 (YouTube Downloader)

一個功能強大的 YouTube 影片下載工具，使用 Python 和 PyQt5 開發，支援多種格式和解析度的下載。

## 版本更新 (V1.64)

- **改進年齡限制影片處理**：優化了對年齡限制影片的檢測和處理流程
- **添加 cookies 支援**：可以使用 cookies.txt 檔案下載年齡限制影片
- **修復多視窗問題**：修復了在處理錯誤時可能出現多個視窗的問題
- **改進錯誤處理**：提供更清晰的錯誤訊息和解決方案

## 主要功能

- **多格式下載**：支援影片、音訊多種格式下載
- **批量下載**：支援多個影片同時下載
- **自訂解析度**：可選擇不同解析度進行下載
- **下載管理**：暫停、繼續、取消下載
- **檔案管理**：瀏覽、刪除、合併已下載檔案
- **自訂設定**：可調整下載路徑、檔案命名、網路設定等
- **年齡限制處理**：支援使用 cookies 下載年齡限制影片

## 系統需求

- Python 3.6+
- PyQt5
- yt-dlp
- FFmpeg (用於合併影片和音訊)

## 安裝方法

1. 克隆此倉庫：
```bash
git clone https://github.com/your-username/youtube-downloader.git
cd youtube-downloader
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 安裝 FFmpeg：
   - Windows: 下載 FFmpeg 並添加到系統 PATH
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

## 使用方法

1. 運行程式：
```bash
python src/tabbed_gui_demo.py
```

2. 在下載頁籤中輸入 YouTube 影片網址
3. 選擇格式和解析度
4. 點擊「開始下載」按鈕

## 下載年齡限制影片

1. 在設定頁籤中的「網路設定」區塊啟用「使用 cookies」選項
2. 選擇有效的 cookies.txt 檔案（可使用瀏覽器擴充功能匯出）
3. 套用設定後重新下載

## 授權

本項目採用 MIT 授權協議 - 詳見 [LICENSE](LICENSE) 檔案

## 貢獻

歡迎提交問題報告和功能請求，也歡迎提交 Pull Request 來改進程式。 