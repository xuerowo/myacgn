#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
替換腳本：將所有 MD 檔案中的特定文字進行替換
替換項目：
- "亞當" → "阿達姆"
- "龍斗小子" → "小龍"
"""

import os
import re
from pathlib import Path

# 獲取當前目錄下所有的 md 檔案（包括子目錄）
def find_md_files(base_dir='.'):
    return list(Path(base_dir).rglob('*.md'))

# 替換文字
def replace_text_in_file(file_path):
    # 讀取檔案內容
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 儲存原始內容以便比較
    original_content = content
    
    # 執行替換
    content = re.sub('亞當', '阿達姆', content)
    content = re.sub('龍斗小子', '小龍', content)
    
    # 如果內容有變化，則寫回檔案
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        return True
    return False

def main():
    # 計數器
    processed_files = 0
    changed_files = 0
    
    # 存儲被修改的檔案列表
    modified_files = []
    
    # 取得所有 md 檔案
    md_files = find_md_files()
    
    # 遍歷每個檔案並進行替換
    for file_path in md_files:
        if replace_text_in_file(file_path):
            print(f"已更新檔案: {file_path}")
            changed_files += 1
            modified_files.append(str(file_path))
        processed_files += 1
    
    # 輸出結果統計
    print(f"\n替換完成！")
    print(f"處理檔案總數: {processed_files}")
    print(f"已更新檔案數: {changed_files}")
    
    # 顯示所有被修改的檔案
    if modified_files:
        print("\n以下檔案已被修改：")
        for i, file_path in enumerate(modified_files, 1):
            print(f"{i}. {file_path}")
    else:
        print("\n沒有檔案被修改")
    
    # 添加暫停，讓用戶能看到結果
    input("\n按Enter鍵退出...")

if __name__ == "__main__":
    main() 