# 通用 GitHub 自動更新工具

這是一個通用的 GitHub 儲存庫自動更新腳本，可以在任何 Git 專案中使用，無需特定配置。

## 🚀 快速開始

### 基本使用
```bash
# 雙擊執行或命令列執行
python 通用自動更新.py
```

### 進階使用
```bash
# 預覽模式（不實際執行）
python 通用自動更新.py --dry-run

# 自定義 commit 訊息
python 通用自動更新.py --message "修復重要bug"

# 推送到指定分支
python 通用自動更新.py --branch develop

# 只處理已暫存的檔案
python 通用自動更新.py --no-add
```

## ✨ 功能特色

### 🎯 智慧 Commit 訊息
腳本會根據檔案變更類型自動生成 GitHub 風格的 commit 訊息：

- **新增檔案**：`"Add files via upload"`
- **修改單一檔案**：`"Update filename.ext"`
- **刪除單一檔案**：`"Delete filename.ext"`
- **多檔案修改**：`"Update content"`
- **多檔案刪除**：`"Delete files"`

### 🛡️ 安全機制
- 自動修復 Git 安全目錄問題
- 預覽模式避免意外提交
- 詳細的錯誤處理和提示
- 支援用戶中斷操作

### 🎨 友好介面
- 彩色控制台輸出
- 清楚的進度顯示
- 詳細的檔案變更列表
- Windows 視窗標題設定

### ⚙️ 自動檢測
- 自動檢測 Git 儲存庫
- 自動獲取遠端 URL 和分支
- 智慧處理檔案編碼問題
- 跨平台相容性

## 📋 命令列選項

| 選項 | 簡寫 | 說明 |
|------|------|------|
| `--dry-run` | - | 預覽模式，顯示變更但不執行 |
| `--message` | `-m` | 自定義 commit 訊息 |
| `--branch` | `-b` | 指定推送分支 |
| `--no-add` | - | 不自動添加檔案，只處理已暫存的 |

## 📁 使用範例

### 日常更新
```bash
# 簡單更新（最常用）
python 通用自動更新.py
```

### 預覽變更
```bash
# 先看看會提交什麼
python 通用自動更新.py --dry-run
```

### 功能開發
```bash
# 推送到開發分支
python 通用自動更新.py --branch feature/new-feature --message "實現新功能"
```

### 緊急修復
```bash
# 快速修復並推送
python 通用自動更新.py --message "修復緊急bug" --branch hotfix
```

## 🔧 系統需求

- Python 3.6+
- Git 已安裝並配置
- 網路連線（用於推送）

## ⚠️ 注意事項

1. **首次使用**：確保已設定 Git 使用者資訊
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

2. **認證設定**：確保已設定 GitHub 認證（SSH Key 或 Personal Access Token）

3. **檔案備份**：重要檔案建議先備份

4. **分支權限**：確認有推送到目標分支的權限

## 🐛 常見問題

### Q: 提示 "dubious ownership" 錯誤
A: 腳本會自動修復此問題，如果仍有問題請手動執行：
```bash
git config --global --add safe.directory /path/to/your/repo
```

### Q: 推送失敗
A: 檢查：
- 網路連線
- GitHub 認證設定
- 分支推送權限
- 遠端分支是否存在

### Q: 中文檔名顯示亂碼
A: 腳本已處理編碼問題，如仍有問題請確認終端編碼設定

## 📝 授權

此腳本為開源軟體，可自由使用和修改。