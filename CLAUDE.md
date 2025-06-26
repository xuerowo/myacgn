# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個 ACGN（動畫、漫畫、遊戲、小說）翻譯網站專案，主要包含：
- 輕小說翻譯功能
- 網漫翻譯功能
- 本地開發伺服器
- 前端 Web 介面
- 簡單的遊戲類頁面

## 核心開發命令

### 啟動開發環境
```bash
python 啟動伺服器.py
```
此命令會：
1. 自動執行內容生成腳本
2. 啟動本地 HTTP 伺服器（預設 port 8000）
3. 自動開啟瀏覽器
4. 支援自動終止舊伺服器程序

### 輕小說內容管理
```bash
# 生成小說資料索引
python 輕小說翻譯/generate_novels.py

# 檢視生成的資料
cat 輕小說翻譯/novels.json
```

### 網漫內容管理
```bash
# 掃描並生成漫畫資料索引
python 網漫翻譯/manga_scanner.py scan

# 檢視漫畫列表
python 網漫翻譯/manga_scanner.py list

# 檢視特定漫畫詳情（索引從1開始）
python 網漫翻譯/manga_scanner.py detail 1
```

## 專案架構

### 前端架構
- **技術棧**: Vue.js 3 + 原生 JavaScript
- **樣式**: 自定義 CSS，支援亮色/暗色主題
- **主要頁面**:
  - `acgntranslate.html` - 主要翻譯頁面
  - `index.html` - 首頁
  - `recommendations.html` - 推薦頁面
  - `commentsection.html` - 評論功能
  - `destiny-game-class.html` - 命運遊戲類頁面
  - `shooting-game.html` - 射擊遊戲頁面

### 後端架構
- **內容生成**: Python 腳本自動解析 Markdown 檔案並生成 JSON 索引
- **本地伺服器**: 自定義 HTTP 伺服器，支援多執行緒和內容壓縮
- **內容儲存**: 
  - Markdown 檔案儲存翻譯內容
  - JSON 檔案儲存元資料和索引

### 內容組織結構

#### 輕小說翻譯
```
輕小說翻譯/
├── generate_novels.py          # 內容生成腳本
├── novels.json                 # 生成的小說索引
├── version.json               # 版本資訊
├── changelog.html             # 更新日誌
└── 《小說標題》/              # 各小說資料夾
    ├── 0 譯名.md             # 譯名對照
    ├── 00 簡介.md            # 小說簡介（包含作者、標籤等）
    ├── 1 章節標題.md         # 章節內容
    └── cover.jpg             # 封面圖片
```

#### 網漫翻譯
```
網漫翻譯/
├── manga_scanner.py           # 漫畫掃描腳本
├── manga.json                 # 生成的漫畫索引
└── 漫畫標題/                 # 各漫畫資料夾
    ├── 簡介.md               # 漫畫簡介
    ├── cover.jpg             # 封面圖片
    └── 1/                    # 章節資料夾（數字命名）
        ├── 1.jpg             # 漫畫頁面
        └── ...
```

## 開發工作流程

1. **內容更新後**：
   - 輕小說：自動執行或手動執行 `generate_novels.py`
   - 網漫：執行 `manga_scanner.py scan`

2. **測試頁面**：
   - 執行 `python 啟動伺服器.py`
   - 選擇要測試的 HTML 檔案

3. **內容格式**：
   - 章節檔案命名：數字開頭（如 `1 標題.md`）
   - 簡介檔案：包含作者、類型、原始連結等資訊
   - 支援特殊章節（如 `45.5 番外篇.md`）

## 特殊注意事項

- **編碼**: 所有檔案使用 UTF-8 編碼，支援繁體中文內容
- **伺服器功能**: 啟動腳本包含智慧型的埠口管理和程序終止功能
- **內容解析**: 自動提取章節編號、清理標題格式、計算字數統計
- **暗色主題**: 前端支援自動暗色主題切換
- **快取控制**: 開發伺服器禁用快取以確保內容即時更新

## 除錯提示

- 如果伺服器啟動失敗，檢查埠口是否被佔用
- 內容不更新時，確認是否執行了相應的生成腳本
- 章節順序錯誤時，檢查檔案命名是否符合數字開頭格式
- 中文顯示問題時，確認檔案編碼為 UTF-8