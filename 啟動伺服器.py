#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地 HTTP 伺服器啟動腳本
用於在本地環境中測試輕小說翻譯網站
支援自動關閉舊伺服器功能
支援選擇HTML檔案功能
"""

import http.server
import socketserver
import webbrowser
import sys
import os
import subprocess
import signal
import time
from pathlib import Path
import threading
from functools import partial
import glob

def kill_process_on_port(port):
    """終止佔用指定埠口的進程"""
    try:
        if os.name == 'nt':  # Windows
            # 使用 netstat 找到佔用埠口的進程
            result = subprocess.run(
                ['netstat', '-ano', '-p', 'TCP'],
                capture_output=True,
                text=True,
                encoding='cp950',  # Windows 繁體中文編碼
                errors='ignore'    # 忽略編碼錯誤
            )
            
            if result.stdout is None:
                return False
                
            lines = result.stdout.split('\n')
            for line in lines:
                if f':{port}' in line and 'LISTENING' in line:
                    parts = line.split()
                    if len(parts) >= 5:
                        pid = parts[-1]
                        try:
                            print(f"🔍 發現佔用埠 {port} 的進程 PID: {pid}")
                            
                            # 找到 cmd.exe 視窗並終止
                            try:
                                # 使用 wmic 找到 python.exe 的父進程鏈
                                # 第一步：找到 python.exe 的父進程（通常是 cmd.exe）
                                wmic_cmd = f'wmic process where "ProcessId={pid}" get ParentProcessId'
                                result = subprocess.run(wmic_cmd, shell=True, capture_output=True, text=True, encoding='cp950', errors='ignore')
                                if result.stdout:
                                    lines = result.stdout.strip().split('\n')
                                    if len(lines) > 1:
                                        cmd_pid = lines[1].strip()
                                        if cmd_pid and cmd_pid.isdigit():
                                            # 第二步：找到 cmd.exe 的父進程（通常是另一個 cmd.exe 或 conhost.exe）
                                            wmic_cmd2 = f'wmic process where "ProcessId={cmd_pid}" get ParentProcessId'
                                            result2 = subprocess.run(wmic_cmd2, shell=True, capture_output=True, text=True, encoding='cp950', errors='ignore')
                                            if result2.stdout:
                                                lines2 = result2.stdout.strip().split('\n')
                                                if len(lines2) > 1:
                                                    console_pid = lines2[1].strip()
                                                    if console_pid and console_pid.isdigit():
                                                        # 終止最上層的 cmd.exe（這會關閉整個終端視窗）
                                                        subprocess.run(['taskkill', '/F', '/T', '/PID', console_pid], 
                                                                     capture_output=True, check=False)
                                            # 如果找不到祖父進程，至少終止父進程
                                            subprocess.run(['taskkill', '/F', '/T', '/PID', cmd_pid], 
                                                         capture_output=True, check=False)
                            except:
                                pass
                            
                            # 終止進程
                            subprocess.run(['taskkill', '/F', '/PID', pid], 
                                         capture_output=True, check=True)
                            print(f"✅ 已成功終止進程 PID: {pid}")
                            time.sleep(1)  # 等待進程完全終止
                            return True
                        except subprocess.CalledProcessError:
                            print(f"⚠️  無法終止進程 PID: {pid}")
        else:  # Unix/Linux/macOS
            # 使用 lsof 找到佔用埠口的進程
            result = subprocess.run(
                ['lsof', '-ti', f':{port}'],
                capture_output=True,
                text=True
            )
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        print(f"🔍 發現佔用埠 {port} 的進程 PID: {pid}")
                        os.kill(int(pid), signal.SIGTERM)
                        print(f"✅ 已成功終止進程 PID: {pid}")
                        time.sleep(1)
                        return True
                    except (ProcessLookupError, ValueError):
                        print(f"⚠️  無法終止進程 PID: {pid}")
                        
    except Exception as e:
        print(f"⚠️  檢查埠口時發生錯誤: {e}")
    
    return False

def check_port_available(port):
    """檢查埠口是否可用"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return True
    except OSError:
        return False

def scan_html_files():
    """掃描當前目錄下的所有HTML檔案"""
    html_files = []
    
    # 使用遞歸掃描，包含當前目錄和子目錄
    for file_path in glob.glob("**/*.html", recursive=True):
        html_files.append(file_path)
    
    # 去除重複項目並排序
    html_files = list(set(html_files))
    return sorted(html_files)

def select_html_file():
    """讓用戶選擇要服務的HTML檔案"""
    html_files = scan_html_files()
    
    if not html_files:
        print("❌ 在當前目錄中找不到任何HTML檔案")
        return None
    
    print("\n📄 發現以下HTML檔案：")
    for i, file_path in enumerate(html_files, 1):
        file_size = os.path.getsize(file_path)
        file_size_kb = file_size / 1024
        print(f"  {i}. {file_path} ({file_size_kb:.1f} KB)")
    
    while True:
        try:
            choice = input(f"請選擇要開啟的HTML檔案 (1-{len(html_files)}): ").strip()
            
            if choice == "":
                print("❌ 請選擇一個檔案，不能為空")
                continue
            
            choice_num = int(choice)
            if 1 <= choice_num <= len(html_files):
                selected_file = html_files[choice_num - 1]
                print(f"✅ 已選擇: {selected_file}")
                return selected_file
            else:
                print(f"❌ 請輸入 1 到 {len(html_files)} 之間的數字")
                
        except ValueError:
            print("❌ 請輸入有效的數字")
        except KeyboardInterrupt:
            print("\n🛑 操作已取消")
            return None

def start_server(port=8000, auto_kill=True, target_file=None):
    """啟動本地 HTTP 伺服器"""
    
    # 確保在正確的目錄中運行
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # 如果沒有指定目標檔案，讓用戶選擇
    if target_file is None:
        target_file = select_html_file()
        if target_file is None:
            return
    
    # 檢查目標檔案是否存在
    if not Path(target_file).exists():
        print(f"❌ 檔案不存在: {target_file}")
        return
    
    # 檢查埠口是否被佔用，如果被佔用且允許自動終止，則終止舊進程
    if not check_port_available(port):
        if auto_kill:
            print(f"🔄 埠 {port} 已被佔用，正在終止舊伺服器...")
            if kill_process_on_port(port):
                print(f"✅ 舊伺服器已終止，正在啟動新伺服器...")
                time.sleep(2)  # 等待埠口釋放
            else:
                print(f"❌ 無法終止佔用埠 {port} 的進程")
                print(f"🔄 嘗試使用埠 {port + 1}")
                return start_server(port + 1, auto_kill, target_file)
        else:
            print(f"❌ 埠 {port} 已被使用")
            print(f"🔄 嘗試使用埠 {port + 1}")
            return start_server(port + 1, auto_kill, target_file)
    
    # 設置處理器，支援 UTF-8 編碼和性能優化
    class OptimizedHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # 設置適當的 MIME 類型和編碼
            if self.path.endswith('.html'):
                self.send_header('Content-Type', 'text/html; charset=utf-8')
            elif self.path.endswith('.js'):
                self.send_header('Content-Type', 'application/javascript; charset=utf-8')
            elif self.path.endswith('.css'):
                self.send_header('Content-Type', 'text/css; charset=utf-8')
            elif self.path.endswith('.json'):
                self.send_header('Content-Type', 'application/json; charset=utf-8')
            elif self.path.endswith('.md'):
                self.send_header('Content-Type', 'text/markdown; charset=utf-8')
            
            # 禁用快取來確保檔案更新立即生效
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            
            # 啟用 gzip 壓縮
            self.send_header('Content-Encoding', 'identity')
            
            super().end_headers()
        
        def log_message(self, format, *args):
            # 隱藏日誌輸出以保持版面乾淨
            pass
    
    # 使用多線程伺服器來提高性能
    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True
        daemon_threads = True
    
    try:
        with ThreadedTCPServer(("", port), OptimizedHTTPRequestHandler) as httpd:
            # 設置終端視窗標題
            if os.name == 'nt':  # Windows
                import ctypes
                try:
                    ctypes.windll.kernel32.SetConsoleTitleW(f'輕小說伺服器 - 運行中 (Port {port})')
                except:
                    # 如果失敗，使用 os.system
                    os.system(f'title 輕小說伺服器 - 運行中 (Port {port})')
            
            print(f"\n✅ 伺服器啟動成功！")
            print(f"\n🌐 開啟網址: http://localhost:{port}/{target_file}")
            print(f"\n🟢 伺服器運行中... Port {port}")
            print(f"\n📁 按 Ctrl+C 停止伺服器\n")
            
            # 自動開啟瀏覽器
            try:
                webbrowser.open(f'http://localhost:{port}/{target_file}')
            except Exception as e:
                print(f"⚠️  無法自動開啟瀏覽器: {e}")
                print(f"請手動訪問: http://localhost:{port}/{target_file}")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print(f"\n🛑 伺服器已停止")
        sys.exit(0)
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ 埠 {port} 仍然被使用")
            print(f"🔄 嘗試使用埠 {port + 1}")
            start_server(port + 1, auto_kill, target_file)
        else:
            print(f"❌ 啟動伺服器失敗: {e}")
            sys.exit(1)

if __name__ == "__main__":
    print("\n🌟 輕小說翻譯本地伺服器")
    
    # 檢查 Python 版本
    if sys.version_info < (3, 6):
        print("❌ 需要 Python 3.6 或更高版本")
        sys.exit(1)
    
    # 先執行 generate_novels.py
    novels_dir = os.path.join(os.path.dirname(__file__), "輕小說翻譯")
    generate_script = os.path.join(novels_dir, "generate_novels.py")
    
    if os.path.exists(generate_script):
        print("📚 正在生成小說列表...")
        try:
            # 將輸出重定向到 DEVNULL 來隱藏
            subprocess.run([sys.executable, generate_script], 
                         cwd=novels_dir, 
                         check=True,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
            print("✅ 小說列表生成完成！\n")
        except subprocess.CalledProcessError as e:
            print(f"❌ 生成小說列表失敗: {e}")
            print("繼續啟動伺服器...\n")
    
    start_server() 