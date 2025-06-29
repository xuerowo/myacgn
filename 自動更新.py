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
import shlex
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

def run_command(command, description, cwd=None, capture_output=False):
    """執行命令並顯示結果"""
    print_colored(f"\n🔄 {description}...", 'cyan')
    try:
        # 對於 Git 命令，確保檔案路徑正確處理
        if isinstance(command, list) and len(command) >= 3 and command[0] == "git" and command[1] == "add":
            # 對 Git add 命令使用特殊處理
            git_add_command = ["git", "add", "--"] + command[2:]  # 添加 -- 分隔符
            command = git_add_command
        
        if capture_output:
            # 需要捕獲輸出的情況（如推送衝突檢測）
            result = subprocess.run(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
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
        else:
            # 即時輸出模式，但仍需捕獲錯誤訊息
            result = subprocess.run(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                shell=True if isinstance(command, str) else False
            )
            
            # 顯示輸出（模擬即時輸出）
            if result.stdout.strip():
                print(result.stdout.strip())
            
            if result.returncode == 0:
                print_colored(f"✅ {description} 完成", 'green')
                return True, result.stdout
            else:
                print_colored(f"❌ {description} 失敗", 'red')
                if result.stderr.strip():
                    print_colored(f"錯誤訊息: {result.stderr.strip()}", 'red')
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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
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
        # 如果檔名不包含引號和轉義序列，直接返回（Git 配置生效的情況）
        if not filename.startswith('"') and '\\' not in filename:
            return filename
        
        # 處理 Git 的引號包圍檔名
        if filename.startswith('"'):
            # 移除引號
            clean_name = filename.strip('"')
            
            # 檢查是否包含八進制轉義序列
            if '\\' in clean_name:
                # 方法1：完整的字節級處理
                try:
                    import re
                    
                    # 分離八進制序列和普通字符
                    parts = re.split(r'(\\[0-7]{3})', clean_name)
                    result_bytes = bytearray()
                    
                    for part in parts:
                        if part.startswith('\\') and len(part) == 4:
                            # 這是八進制序列 \xxx
                            octal_val = int(part[1:], 8)
                            result_bytes.append(octal_val)
                        else:
                            # 這是普通字符
                            result_bytes.extend(part.encode('utf-8'))
                    
                    # 嘗試解碼整個字節序列
                    return result_bytes.decode('utf-8')
                    
                except Exception:
                    pass
                
                # 方法2：使用正則表達式逐個替換
                try:
                    import re
                    
                    def octal_to_byte(match):
                        octal_str = match.group(1)
                        byte_val = int(octal_str, 8)
                        return bytes([byte_val])
                    
                    # 替換所有八進制序列為字節
                    result = clean_name
                    byte_parts = []
                    last_end = 0
                    
                    for match in re.finditer(r'\\([0-7]{3})', clean_name):
                        # 添加匹配前的普通文字
                        if match.start() > last_end:
                            byte_parts.append(clean_name[last_end:match.start()].encode('utf-8'))
                        
                        # 添加八進制字節
                        octal_val = int(match.group(1), 8)
                        byte_parts.append(bytes([octal_val]))
                        
                        last_end = match.end()
                    
                    # 添加剩餘的普通文字
                    if last_end < len(clean_name):
                        byte_parts.append(clean_name[last_end:].encode('utf-8'))
                    
                    # 合併所有字節並解碼
                    full_bytes = b''.join(byte_parts)
                    return full_bytes.decode('utf-8')
                    
                except Exception:
                    pass
                
                # 方法3：簡化的 unicode_escape 方法
                try:
                    # 直接使用 Python 的內建解碼
                    decoded = clean_name.encode('latin1').decode('unicode_escape')
                    return decoded.encode('latin1').decode('utf-8')
                except Exception:
                    pass
                
                # 方法4：最後的備用方法
                try:
                    decoded = clean_name.encode().decode('unicode_escape')
                    return decoded
                except Exception:
                    pass
            
            # 沒有轉義序列，直接返回清理後的名稱
            return clean_name
        
        # 沒有引號，直接返回原始檔名
        return filename
        
    except Exception:
        # 所有方法都失敗，返回原始檔名
        return original_filename

def should_ignore_file(filename):
    """判斷是否應該忽略特定檔案"""
    import re
    
    # 解碼檔名以正確處理中文路徑
    decoded_filename = decode_filename(filename)
    
    ignore_patterns = [
        # Claude Code 相關檔案
        r'^\.claude/',
        r'^CLAUDE\.md$',
        # 常見的臨時檔案和系統檔案
        r'\.tmp$', r'\.temp$', r'~$',
        r'Thumbs\.db$', r'\.DS_Store$',
        r'\.swp$', r'\.swo$', r'\.bak$', r'\.orig$',
        # 編輯器配置
        r'^\.vscode/', r'^\.idea/',
        # Node.js 和 Python 相關
        r'^node_modules/', r'^__pycache__/',
        # 日誌檔案
        r'\.log$', r'\.pid$'
    ]
    
    for pattern in ignore_patterns:
        if re.search(pattern, decoded_filename, re.IGNORECASE):
            return True
    return False

def filter_git_status(git_status):
    """過濾 Git 狀態，移除應忽略的檔案"""
    if not git_status.strip():
        return git_status, []
    
    lines = git_status.strip().split('\n')
    filtered_lines = []
    ignored_files = []
    
    for line in lines:
        if len(line) < 3:
            continue
            
        # Git --porcelain 格式：正確解析狀態和檔名
        if len(line) >= 3 and line[2] == ' ':
            # 標準格式：XY filename
            filename = line[3:]
        else:
            # 可能是簡化格式，需要找到第一個空格
            space_index = line.find(' ')
            if space_index > 0:
                filename = line[space_index + 1:]
            else:
                continue
        
        if should_ignore_file(filename):
            ignored_files.append(decode_filename(filename))
        else:
            filtered_lines.append(line)
    
    return '\n'.join(filtered_lines), ignored_files

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
            
        # Git --porcelain 格式：正確解析狀態和檔名
        if len(line) >= 3 and line[2] == ' ':
            # 標準格式：XY filename
            status = line[:2].strip()
            filename = line[3:]
        else:
            # 可能是簡化格式，需要找到第一個空格
            space_index = line.find(' ')
            if space_index > 0:
                status = line[:space_index].strip()
                filename = line[space_index + 1:]
            else:
                continue
        
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
            filename = os.path.basename(added_files[0])
            return f"Add {filename}"
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
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
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
                stdout=subprocess.DEVNULL,  # 隱藏詳細輸出
                stderr=subprocess.PIPE,     # 捕獲錯誤
                text=True,
                encoding='utf-8',
                errors='ignore'
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
        "檢查 Git 狀態",
        capture_output=True
    )
    
    # 如果 Git 狀態檢查失敗，嘗試修復安全目錄問題
    if not success:
        if "dubious ownership" in git_status.lower():
            print_colored("🔍 檢測到 Git 安全目錄問題，正在修復...", 'yellow')
            if fix_git_safe_directory():
                # 重新嘗試檢查 Git 狀態
                success, git_status = run_command(
                    ["git", "status", "--porcelain"],
                    "重新檢查 Git 狀態",
                    capture_output=True
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
    
    # 過濾 Git 狀態，移除應忽略的檔案
    filtered_git_status, ignored_files = filter_git_status(git_status)
    
    # 顯示被忽略的檔案
    if ignored_files:
        print_colored(f"\n🚫 自動忽略 {len(ignored_files)} 個檔案:", 'purple')
        for ignored_file in ignored_files:
            print_colored(f"   🔒 忽略: {ignored_file}", 'purple')
    
    if not filtered_git_status.strip():
        if ignored_files:
            print_colored("✨ 所有變更檔案都被自動忽略，無需更新", 'green')
        else:
            print_colored("✨ 沒有檔案變更，無需更新", 'green')
        input("\n按 Enter 鍵結束...")
        return
    
    # 顯示將要處理的變更檔案
    print_colored(f"\n📋 檢測到 {len(filtered_git_status.strip().split(chr(10)))} 個檔案變更:", 'yellow')
    for line in filtered_git_status.strip().split('\n'):
        if len(line) < 3:
            continue
            
        # Git --porcelain 格式：前兩個字符是狀態，第三個字符是空格，之後是檔名
        # 但有時第一個字符是狀態，第二個是空格，所以需要正確解析
        if len(line) >= 3 and line[2] == ' ':
            # 標準格式：XY filename
            status = line[:2]
            filename = line[3:]
        else:
            # 可能是簡化格式，需要找到第一個空格
            space_index = line.find(' ')
            if space_index > 0:
                status = line[:space_index]
                filename = line[space_index + 1:]
            else:
                continue
        
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
    
    # 步驟 3: 添加所有變更檔案（使用 git add . 以避免路徑問題）
    if filtered_git_status.strip():
        success, _ = run_command(
            ["git", "add", "."],
            "添加所有變更檔案到暫存區",
            capture_output=False
        )
        
        if success:
            # 移除被忽略的檔案（如果有的話）
            if ignored_files:
                for ignored_file in ignored_files:
                    # 嘗試移除被忽略的檔案從暫存區
                    success_reset, _ = run_command(
                        ["git", "reset", "HEAD", ignored_file],
                        f"移除被忽略的檔案: {ignored_file}",
                        capture_output=True  # 這裡不需要顯示輸出
                    )
                    # 忽略 reset 失敗（可能檔案本來就不在暫存區）
            
            # 統計檔案數量
            file_count = len([line for line in filtered_git_status.strip().split('\n') if len(line) >= 3])
            print_colored(f"✅ 成功添加 {file_count} 個檔案到暫存區", 'green')
        else:
            print_colored("❌ 添加檔案失敗", 'red')
            input("\n按 Enter 鍵結束...")
            return
    else:
        print_colored("❌ 沒有檔案需要添加", 'red')
        input("\n按 Enter 鍵結束...")
        return
    
    # 步驟 4: 檢查暫存區狀態並提交變更
    # 先檢查暫存區是否有內容
    success_staged, staged_output = run_command(
        ["git", "diff", "--cached", "--name-only"],
        "檢查暫存區狀態",
        capture_output=True
    )
    
    if not success_staged or not staged_output.strip():
        print_colored("⚠️  暫存區為空，無法提交", 'yellow')
        print_colored("📝 這可能是因為所有變更都被忽略或已經提交", 'cyan')
        input("\n按 Enter 鍵結束...")
        return
    
    commit_message = generate_commit_message(filtered_git_status)
    print_colored(f"📝 Commit 訊息: {commit_message}", 'cyan')
    
    success, commit_output = run_command(
        ["git", "commit", "-m", commit_message],
        "提交變更",
        capture_output=False
    )
    
    if not success:
        print_colored("❌ 提交變更失敗", 'red')
        input("\n按 Enter 鍵結束...")
        return
    
    # 步驟 5: 推送到 GitHub
    success, _ = run_command(
        ["git", "push", "origin", "main"],
        "推送到 GitHub",
        capture_output=False
    )
    
    if success:
        print_colored("\n🎉 成功更新到 GitHub!", 'green')
        print_colored("🔗 儲存庫: https://github.com/xuerowo/myacgn", 'cyan')
    else:
        print_colored("\n❌ 推送到 GitHub 失敗", 'red')
        print_colored("📝 提交已儲存在本地，但未推送到 GitHub", 'yellow')
        print_colored("\n🔧 認證設定方法:", 'cyan')
        print_colored("1. 設定 Personal Access Token:", 'white')
        print_colored("   git config --global credential.helper store", 'white')
        print_colored("   然後手動執行: git push origin main", 'white')
        print_colored("\n2. 或者使用 SSH 金鑰（建議）", 'white')
        print_colored("\n3. 手動推送本地提交:", 'white')
        print_colored("   git push origin main", 'white')
        
        # 顯示本地領先的提交
        success_log, log_output = run_command(
            ["git", "log", "--oneline", "origin/main..HEAD"],
            "檢查未推送的提交",
            capture_output=True
        )
        if success_log and log_output.strip():
            print_colored("\n📋 本地未推送的提交:", 'cyan')
            for line in log_output.strip().split('\n'):
                if line.strip():
                    print_colored(f"   {line}", 'yellow')
    
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