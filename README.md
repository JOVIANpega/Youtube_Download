# YouTube 影片下載器 / YouTube Video Downloader

**版本 / Version / バージョン / 버전: V1.0**

一個功能強大的 YouTube 影片下載工具，支援多種格式和品質選擇。

## 版本歷史 / Version History / バージョン履歴 / 버전 히스토리

### V1.0 (2024-12-19)
- 🎉 **初始版本發布** / Initial Release / 初回リリース / 초기 릴리스
- 🎥 支援多種影片格式下載
- 🌍 多語言介面支援 (中文、英文、日文、韓文)
- 📁 自訂下載路徑功能
- 📊 即時進度顯示
- 🎵 音訊轉換功能 (MP3/WAV)
- 🔄 背景下載不阻塞 UI
- 🛠️ SSL 證書問題修復
- 📝 完整的錯誤處理機制
- ⚙️ 用戶偏好設定管理
- 🎯 年齡限制影片處理
- 📋 下載歷史記錄
- 🔧 多個備用版本 (PySide6, 簡化 GUI, 命令行)

## 功能特色 / Features / 機能 / 기능

- 🎥 **多格式支援**: 支援影片和音訊下載
- 🌍 **多語言介面**: 中文、英文、日文、韓文
- 📁 **自訂下載路徑**: 可選擇下載位置
- 📊 **即時進度顯示**: 顯示下載進度和速度
- 🎵 **音訊轉換**: 支援 MP3 和 WAV 格式
- 🔄 **背景下載**: 不阻塞使用者介面

## 支援的格式 / Supported Formats / 対応形式 / 지원 형식

- **預設品質**: 自動選擇最佳品質
- **最高品質影片**: 下載最高畫質影片
- **僅音訊 (MP3)**: 轉換為 MP3 格式
- **僅音訊 (WAV)**: 轉換為 WAV 格式

## 安裝說明 / Installation / インストール / 설치

### 1. 安裝依賴 / Install Dependencies

```bash
# 運行安裝腳本
python install_dependencies.py
```

或者手動安裝：

```bash
# 安裝 Python 依賴
pip install -r requirements.txt

# 安裝 FFmpeg (必需)
# Windows: 下載並添加到 PATH
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### 2. 運行應用程式 / Run Application

```bash
python src/main.py
```

## 使用說明 / Usage / 使用方法 / 사용법

1. **輸入 URL**: 在輸入框中貼上 YouTube 影片網址
2. **選擇格式**: 從下拉選單選擇下載格式
3. **設定路徑**: 選擇下載資料夾 (預設為 Downloads)
4. **開始下載**: 點擊下載按鈕開始下載
5. **監控進度**: 在日誌區域查看下載進度

## 專案結構 / Project Structure / プロジェクト構造 / 프로젝트 구조

```
project/
├── src/                    # 源代碼目錄
│   ├── main.py            # 主程式入口
│   └── ui/                # UI 相關文件
│       └── main_window.py # 主視窗
├── requirements.txt       # Python 依賴
├── install_dependencies.py # 依賴安裝腳本
└── README.md             # 專案說明
```

## 開發規則 / Development Rules / 開発ルール / 개발 규칙

### 1. 代碼風格 / Code Style / コーディングスタイル / 코딩 스타일
- 遵循 PEP 8 規範
- 使用 4 個空格進行縮排
- 類名使用 PascalCase
- 函數和變量使用 snake_case
- 常量使用大寫字母和下劃線

### 2. UI 開發規範 / UI Development / UI開発 / UI 개발
- 使用 PyQt6 進行 UI 開發
- 將 UI 邏輯和業務邏輯分離
- 使用信號槽機制進行組件通信
- 支援多語言介面

### 3. 打包規則 / Packaging / パッケージング / 패키징
- 使用 PyInstaller 進行打包
- 打包命令：`pyinstaller --windowed --icon=resources/icon.ico src/main.py`
- 確保所有資源文件都被正確打包

### 4. 版本控制 / Version Control / バージョン管理 / 버전 관리
- 使用 Git 進行版本控制
- 提交信息要清晰描述更改內容
- 重要功能開發使用分支

### 5. 測試規範 / Testing / テスト / 테스트
- 編寫單元測試
- 測試文件放在 `tests/` 目錄
- 測試覆蓋率要求 > 80%

## 開發流程 / Development Workflow / 開発フロー / 개발 워크플로우

1. 克隆專案 / Clone project / プロジェクトをクローン / 프로젝트 클론
2. 安裝依賴 / Install dependencies / 依存関係をインストール / 의존성 설치
3. 運行開發環境 / Run development environment / 開発環境を実行 / 개발 환경 실행
4. 打包應用 / Package application / アプリケーションをパッケージ / 애플리케이션 패키징

## 注意事項 / Notes / 注意事項 / 주의사항

- 確保所有依賴都在 requirements.txt 中列出
- 定期更新依賴版本
- 保持代碼文檔的更新
- 遵循錯誤處理最佳實踐
- 遵守 YouTube 服務條款和版權法規
- 僅下載您有權訪問的內容

## 法律聲明 / Legal Notice / 法的声明 / 법적 고지

本工具僅供個人學習和研究使用。使用者應遵守當地法律法規和 YouTube 服務條款。開發者不對使用者的行為承擔責任。

## 技術支援 / Support / サポート / 지원

如有問題或建議，請提交 Issue 或 Pull Request。

---

**免責聲明**: 請確保您有權下載相關內容，並遵守版權法規。 