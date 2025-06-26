#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ACGN 翻譯自動更新腳本
雙擊執行，自動更新 GitHub 儲存庫
"""

import os
import sys
import subprocess
import time
import locale
from pathlib import Path

def print_colored(text, color='white'):
    """打印彩色文字"""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'purple': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, colors['white'])}{text}{colors['reset']}")

def setup_console_encoding():
    """設置控制台編碼為 UTF-8"""
    if os.name == 'nt':  # Windows
        try:
            # 設置控制台代碼頁為 UTF-8
            os.system('chcp 65001 >nul 2>&1')
            # 設置 Python 的標準輸出編碼
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
        except:
            pass
    
    # 設置 locale
    try:
        locale.setlocale(locale.LC_ALL, '')
    except:
        pass

def set_window_title(title):
    """設置終端視窗標題"""
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            ctypes.windll.kernel32.SetConsoleTitleW(title)
        except:
            os.system(f'title {title}')

def run_command(command, description, cwd=None):
    """執行命令並顯示結果"""
    print_colored(f"\n🔄 {description}...", 'cyan')
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore',
            shell=True if isinstance(command, str) else False
        )
        
        if result.returncode == 0:
            print_colored(f"✅ {description} 完成", 'green')
            if result.stdout.strip():
                print(result.stdout.strip())
            return True, result.stdout
        else:
            print_colored(f"❌ {description} 失敗", 'red')
            if result.stderr.strip():
                print_colored(result.stderr.strip(), 'red')
            return False, result.stderr
    except Exception as e:
        print_colored(f"❌ 執行 {description} 時發生錯誤: {e}", 'red')
        return False, str(e)

def fix_git_safe_directory():
    """修復 Git 安全目錄問題"""
    script_dir = Path(__file__).parent
    try:
        # 添加當前目錄到 Git 安全目錄列表
        result = subprocess.run(
            ["git", "config", "--global", "--add", "safe.directory", str(script_dir)],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='ignore'
        )
        if result.returncode == 0:
            print_colored("🔧 已修復 Git 安全目錄設定", 'green')
            return True
        else:
            print_colored("⚠️  無法修復 Git 安全目錄設定", 'yellow')
            return False
    except Exception as e:
        print_colored(f"⚠️  修復 Git 安全目錄時發生錯誤: {e}", 'yellow')
        return False

def decode_filename(filename):
    """解碼檔案名稱，處理各種編碼情況"""
    if not filename:
        return filename
    
    original_filename = filename
    
    try:
        # 處理 Git 的引號包圍檔名
        if filename.startswith('"'):
            # 移除引號
            filename = filename.strip('"')
            
            # 檢查是否包含八進制轉義序列
            if '\\' in filename:
                # 終極方法：使用 codecs 解碼八進制序列
                try:
                    # 將八進制序列轉換為原始字節
                    import re
                    import codecs
                    
                    # 替換八進制序列為實際字節
                    def octal_replacer(match):
                        octal_str = match.group(1)
                        byte_val = int(octal_str, 8)
                        return chr(byte_val)
                    
                    # 處理所有八進制序列
                    decoded = re.sub(r'\\([0-7]{3})', octal_replacer, filename)
                    
                    # 嘗試將結果編碼為 bytes 然後解碼為 UTF-8
                    byte_data = decoded.encode('latin1')
                    result = byte_data.decode('utf-8')
                    return result
                    
                except Exception:
                    pass
                
                # 備用方法：直接使用 Python 的字節串解碼
                try:
                    # 將 \351\200\232 格式轉換為 Python bytes 字面量
                    import re
                    
                    # 構建字節序列
                    byte_pattern = r'\\([0-7]{3})'
                    matches = re.findall(byte_pattern, filename)
                    
                    if matches:
                        # 創建字節數組
                        byte_values = [int(match, 8) for match in matches]
                        
                        # 找到非八進制部分
                        non_octal_parts = re.split(byte_pattern, filename)
                        
                        # 重建字符串：非八進制部分 + 解碼的字節
                        result_parts = []
                        byte_index = 0
                        
                        for i, part in enumerate(non_octal_parts):
                            if i % 2 == 0:  # 非八進制部分
                                result_parts.append(part)
                            else:  # 這是八進制值，跳過（已在 byte_values 中處理）
                                pass
                        
                        # 解碼字節序列
                        try:
                            decoded_text = bytes(byte_values).decode('utf-8')
                            # 將解碼的文字插入到正確位置
                            # 簡化：假設所有八進制序列都是連續的
                            first_octal_pos = filename.find('\\')
                            if first_octal_pos >= 0:
                                prefix = filename[:first_octal_pos]
                                # 找到八進制序列後的部分
                                remaining = filename
                                for _ in range(len(byte_values)):
                                    # 移除一個八進制序列 \xxx
                                    remaining = re.sub(r'\\[0-7]{3}', '', remaining, count=1)
                                
                                return prefix + decoded_text + remaining
                        except UnicodeDecodeError:
                            pass
                except Exception:
                    pass
                
                # 最後嘗試：標準解碼方法
                try:
                    # 嘗試 unicode_escape
                    decoded = filename.encode().decode('unicode_escape')
                    return decoded
                except:
                    try:
                        # 嘗試 raw_unicode_escape
                        decoded = filename.encode().decode('raw_unicode_escape')
                        return decoded
                    except:
                        pass
        
        # 如果沒有引號或所有解碼都失敗，返回處理後的字符串
        return filename if filename != original_filename else original_filename
        
    except Exception:
        # 最終回退到原始字符串
        return original_filename

def generate_commit_message(git_status):
    """根據 Git 狀態生成 GitHub 風格的 commit 訊息"""
    if not git_status.strip():
        return "Update content"
    
    lines = git_status.strip().split('\n')
    added_files = []
    modified_files = []
    deleted_files = []
    
    for line in lines:
        if len(line) < 3:
            continue
            
        status = line[:2].strip()
        filename = line[3:]
        
        # 解碼檔名
        decoded_filename = decode_filename(filename)
        
        if status in ['A', '??']:
            added_files.append(decoded_filename)
        elif status == 'M':
            modified_files.append(decoded_filename)
        elif status == 'D':
            deleted_files.append(decoded_filename)
    
    # 根據變更類型生成訊息
    total_changes = len(added_files) + len(modified_files) + len(deleted_files)
    
    if total_changes == 1:
        # 單一檔案變更
        if added_files:
            return "Add files via upload"
        elif modified_files:
            filename = os.path.basename(modified_files[0])
            return f"Update {filename}"
        elif deleted_files:
            filename = os.path.basename(deleted_files[0])
            return f"Delete {filename}"
    
    # 多檔案變更或混合變更
    if added_files and not modified_files and not deleted_files:
        return "Add files via upload"
    elif modified_files and not added_files and not deleted_files:
        return "Update content"
    elif deleted_files and not added_files and not modified_files:
        return "Delete files"
    else:
        # 混合變更
        return "Update content"

def setup_git_encoding():
    """設置 Git 編碼配置，避免檔名轉義"""
    try:
        # 設置 Git 不要轉義檔案路徑
        subprocess.run(
            ["git", "config", "core.quotePath", "false"],
            capture_output=True,
            check=True
        )
        print_colored("🔧 已設定 Git 編碼配置", 'green')
    except:
        # 如果設定失敗，不影響主要功能
        pass

def main():
    """主要執行函數"""
    # 設置控制台編碼
    setup_console_encoding()
    
    # 設置 Git 編碼
    setup_git_encoding()
    
    # 設置視窗標題
    set_window_title("ACGN翻譯 - 自動更新")
    
    print_colored("=" * 60, 'blue')
    print_colored("🌟 ACGN 翻譯自動更新工具", 'blue')
    print_colored("=" * 60, 'blue')
    
    # 確保在正確的目錄中運行
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    print_colored(f"📁 工作目錄: {script_dir}", 'yellow')
    
    # 步驟 1: 生成輕小說索引
    novels_script = script_dir / "輕小說翻譯" / "generate_novels.py"
    if novels_script.exists():
        print_colored("\n🔄 生成輕小說索引...", 'cyan')
        try:
            result = subprocess.run(
                [sys.executable, str(novels_script)],
                cwd=script_dir / "輕小說翻譯",
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                stdout=subprocess.DEVNULL,  # 隱藏詳細輸出
                stderr=subprocess.PIPE
            )
            
            if result.returncode == 0:
                print_colored("✅ 生成輕小說索引 完成", 'green')
            else:
                print_colored("⚠️  生成索引失敗，但繼續執行更新流程", 'yellow')
                if result.stderr.strip():
                    print_colored(f"錯誤詳情: {result.stderr.strip()}", 'red')
        except Exception as e:
            print_colored(f"⚠️  執行生成腳本時發生錯誤: {e}", 'yellow')
    else:
        print_colored("⚠️  找不到輕小說生成腳本，跳過索引生成", 'yellow')
    
    # 步驟 2: 檢查 Git 狀態
    success, git_status = run_command(
        ["git", "status", "--porcelain"],
        "檢查 Git 狀態"
    )
    
    # 如果 Git 狀態檢查失敗，嘗試修復安全目錄問題
    if not success:
        if "dubious ownership" in git_status.lower():
            print_colored("🔍 檢測到 Git 安全目錄問題，正在修復...", 'yellow')
            if fix_git_safe_directory():
                # 重新嘗試檢查 Git 狀態
                success, git_status = run_command(
                    ["git", "status", "--porcelain"],
                    "重新檢查 Git 狀態"
                )
                if not success:
                    print_colored("❌ 修復後仍然無法檢查 Git 狀態", 'red')
                    input("\n按 Enter 鍵結束...")
                    return
            else:
                print_colored("❌ 無法修復 Git 安全目錄問題", 'red')
                input("\n按 Enter 鍵結束...")
                return
        else:
            print_colored("❌ Git 狀態檢查失敗", 'red')
            input("\n按 Enter 鍵結束...")
            return
    
    if not git_status.strip():
        print_colored("✨ 沒有檔案變更，無需更新", 'green')
        input("\n按 Enter 鍵結束...")
        return
    
    # 顯示變更的檔案
    print_colored("\n📋 檢測到以下檔案變更:", 'yellow')
    for line in git_status.strip().split('\n'):
        if len(line) < 3:
            continue
            
        status = line[:2]
        filename = line[3:]
        
        # 解碼檔名以正確顯示中文
        display_filename = decode_filename(filename)
        
        if status.strip() == 'M':
            print_colored(f"   📝 修改: {display_filename}", 'yellow')
        elif status.strip() == 'A':
            print_colored(f"   ➕ 新增: {display_filename}", 'green')
        elif status.strip() == 'D':
            print_colored(f"   ❌ 刪除: {display_filename}", 'red')
        elif status.strip() == '??':
            print_colored(f"   🆕 未追蹤: {display_filename}", 'cyan')
        else:
            print_colored(f"   {status.strip()} {display_filename}", 'white')
    
    # 步驟 3: 添加所有變更
    success, _ = run_command(
        ["git", "add", "."],
        "添加所有變更到暫存區"
    )
    
    if not success:
        print_colored("❌ 添加檔案到暫存區失敗", 'red')
        input("\n按 Enter 鍵結束...")
        return
    
    # 步驟 4: 生成 commit 訊息並提交變更
    commit_message = generate_commit_message(git_status)
    print_colored(f"📝 Commit 訊息: {commit_message}", 'cyan')
    
    success, _ = run_command(
        ["git", "commit", "-m", commit_message],
        "提交變更"
    )
    
    if not success:
        print_colored("❌ 提交變更失敗", 'red')
        input("\n按 Enter 鍵結束...")
        return
    
    # 步驟 5: 推送到 GitHub
    success, _ = run_command(
        ["git", "push", "origin", "main"],
        "推送到 GitHub"
    )
    
    if success:
        print_colored("\n🎉 成功更新到 GitHub!", 'green')
        print_colored("🔗 儲存庫: https://github.com/xuerowo/myacgn", 'cyan')
    else:
        print_colored("\n❌ 推送到 GitHub 失敗", 'red')
        print_colored("請檢查網路連線和 Git 認證設定", 'yellow')
    
    print_colored("\n" + "=" * 60, 'blue')
    print_colored("🏁 自動更新流程完成", 'blue')
    print_colored("=" * 60, 'blue')
    
    input("\n按 Enter 鍵結束...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n🛑 用戶中斷操作", 'yellow')
        input("按 Enter 鍵結束...")
    except Exception as e:
        print_colored(f"\n❌ 發生未預期的錯誤: {e}", 'red')
        input("按 Enter 鍵結束...")