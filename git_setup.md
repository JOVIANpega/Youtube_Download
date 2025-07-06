# Git 設置和 GitHub 提交指南

以下是將此專案提交到 GitHub 的步驟：

## 1. 初始化 Git 倉庫

```bash
# 初始化 Git 倉庫
git init

# 添加所有文件到暫存區
git add .

# 提交初始版本
git commit -m "初始提交：YouTube 下載器 V1.64 - 改進年齡限制處理"
```

## 2. 連接到 GitHub

```bash
# 創建 GitHub 倉庫後，添加遠程倉庫
git remote add origin https://github.com/your-username/youtube-downloader.git

# 推送到 GitHub
git push -u origin main
```

如果你的默認分支是 `master` 而不是 `main`，請使用：

```bash
git push -u origin master
```

## 3. 後續更新

每次修改後，可以使用以下命令提交更新：

```bash
# 查看修改狀態
git status

# 添加修改的文件
git add .

# 提交修改
git commit -m "更新：簡短的更新描述"

# 推送到 GitHub
git push
```

## 4. 創建版本標籤

為重要版本創建標籤：

```bash
# 創建標籤
git tag -a v1.64 -m "版本 1.64 - 改進年齡限制處理"

# 推送標籤到 GitHub
git push origin v1.64
```

## 5. 分支管理

創建功能分支進行開發：

```bash
# 創建並切換到新分支
git checkout -b feature/new-feature

# 開發完成後合併回主分支
git checkout main
git merge feature/new-feature

# 刪除已合併的分支
git branch -d feature/new-feature
```

## 注意事項

- 確保 `.gitignore` 文件正確配置，避免提交不必要的文件
- 定期提交代碼，保持提交信息清晰明確
- 在合併前先拉取最新代碼：`git pull origin main` 