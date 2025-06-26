#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
調試編碼問題的測試腳本
"""

import subprocess
import re

def decode_filename(filename):
    """解碼檔案名稱，處理各種編碼情況"""
    print(f"DEBUG: 輸入檔名: '{filename}' (長度: {len(filename)})")
    print(f"DEBUG: 檔名字節: {filename.encode('utf-8')}")
    print(f"DEBUG: 檔名 repr: {repr(filename)}")
    
    if not filename:
        return filename
    
    original_filename = filename
    
    try:
        # 如果檔名不包含引號和轉義序列，直接返回（Git 配置生效的情況）
        if not filename.startswith('"') and '\\' not in filename:
            print("DEBUG: 檔名無引號和轉義序列，直接返回")
            return filename
        
        print("DEBUG: 檔名包含引號或轉義序列，開始處理")
        
        # 處理 Git 的引號包圍檔名
        if filename.startswith('"'):
            print("DEBUG: 檔名以引號開始")
            # 移除引號
            clean_name = filename.strip('"')
            print(f"DEBUG: 移除引號後: '{clean_name}'")
            
            # 檢查是否包含八進制轉義序列
            if '\\' in clean_name:
                print("DEBUG: 發現轉義序列，開始解碼")
                # 方法1：完整的字節級處理
                try:
                    # 分離八進制序列和普通字符
                    parts = re.split(r'(\\[0-7]{3})', clean_name)
                    print(f"DEBUG: 分離後的部分: {parts}")
                    result_bytes = bytearray()
                    
                    for part in parts:
                        if part.startswith('\\') and len(part) == 4:
                            # 這是八進制序列 \xxx
                            octal_val = int(part[1:], 8)
                            print(f"DEBUG: 八進制 {part} -> {octal_val}")
                            result_bytes.append(octal_val)
                        else:
                            # 這是普通字符
                            print(f"DEBUG: 普通字符: '{part}'")
                            result_bytes.extend(part.encode('utf-8'))
                    
                    # 嘗試解碼整個字節序列
                    result = result_bytes.decode('utf-8')
                    print(f"DEBUG: 解碼結果: '{result}'")
                    return result
                    
                except Exception as e:
                    print(f"DEBUG: 方法1失敗: {e}")
                    pass
            
            # 沒有轉義序列，直接返回清理後的名稱
            print("DEBUG: 無轉義序列，返回清理後的名稱")
            return clean_name
        
        # 沒有引號，直接返回原始檔名
        print("DEBUG: 無引號，返回原始檔名")
        return filename
        
    except Exception as e:
        print(f"DEBUG: 異常發生: {e}")
        # 所有方法都失敗，返回原始檔名
        return original_filename

def test_git_status():
    """測試 Git 狀態輸出"""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        
        if result.returncode == 0:
            print("Git 狀態輸出:")
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if len(line) >= 3:
                    status = line[:2]
                    filename = line[3:]
                    print(f"原始: '{line}'")
                    print(f"狀態: '{status}', 檔名: '{filename}'")
                    
                    # 測試解碼
                    decoded = decode_filename(filename)
                    print(f"解碼後: '{decoded}'")
                    print("-" * 50)
        
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    print("開始調試編碼問題...")
    test_git_status()