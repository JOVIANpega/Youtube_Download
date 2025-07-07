# 多平台影片下載器 V1.71 發布說明

發布日期: 2025-07-07

## 新功能

### 1. 視窗大小記憶功能
- 程式現在會記住用戶上次調整的視窗大小和位置
- 下次啟動時會自動套用上次的設定
- 支援跨會話保存視窗設定

### 2. 改進的錯誤處理機制
- 在錯誤對話框中添加紅色平台下載按鈕
- 根據不同平台顯示對應的下載工具按鈕
- 支援 YouTube、TikTok、Instagram、Facebook、Twitter/X、Bilibili 等多個平台

### 3. 更新外部下載工具
- 將 Instagram 下載工具更新為 SaveClip.app
- 提供更好的 Instagram 視頻、照片、Reels、Stories 和 IGTV 下載體驗
- 支援繁體中文界面

## 錯誤修復
- 修復了某些情況下 yt-dlp 下載失敗時沒有顯示錯誤按鈕的問題
- 修復了 QWaitCondition 和 QMutex 相關的錯誤
- 修復了 DownloadTab 類中缺少的方法

## 其他改進
- 代碼優化和性能提升
- 改進了日誌記錄
- 界面細節優化

## 已知問題
- 某些加密的 YouTube 視頻可能無法下載
- 需要登入的私人內容需要提供 cookies.txt 才能下載 