import os
import json
import re
import argparse
from datetime import datetime

def scan_manga_folders(output_file="manga.json", verbose=False):
    """掃描當前目錄下的所有漫畫資料夾並解析資訊"""
    
    # 獲取當前目錄
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 尋找所有資料夾（排除隱藏資料夾和特定資料夾）
    manga_folders = [f for f in os.listdir(current_dir) 
                    if os.path.isdir(os.path.join(current_dir, f)) 
                    and not f.startswith('.') 
                    and f != "__pycache__"]
    
    manga_data = {"manga": []}
    
    for folder in manga_folders:
        if verbose:
            print(f"正在處理：{folder}")
        manga_info = parse_manga_folder(os.path.join(current_dir, folder), verbose)
        if manga_info:
            manga_data["manga"].append(manga_info)
    
    # 將資訊寫入 JSON 檔案
    output_path = os.path.join(current_dir, output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manga_data, f, ensure_ascii=False, indent=2)
    
    print(f"掃描完成，共找到 {len(manga_data['manga'])} 部漫畫")
    print(f"結果已保存到 {output_path}")
    
    return manga_data

def get_folder_modified_time(folder_path):
    """獲取資料夾的最後修改時間"""
    timestamp = os.path.getmtime(folder_path)
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def parse_manga_folder(folder_path, verbose=False):
    """解析漫畫資料夾，獲取簡介和章節資訊"""
    
    folder_name = os.path.basename(folder_path)
    
    # 檢查是否有簡介檔案
    intro_file = os.path.join(folder_path, "@簡介.md")
    if not os.path.exists(intro_file):
        intro_file = os.path.join(folder_path, "簡介.md")
        if not os.path.exists(intro_file):
            if verbose:
                print(f"警告：{folder_name} 資料夾中找不到簡介檔案")
            return None
    
    # 解析簡介檔案
    manga_info = {
        "title": folder_name,
        "cover": f"https://raw.githubusercontent.com/xuerowo/myacgn/main/網漫翻譯/{folder_name}/cover.jpg",
        "r2Url": f"https://pub-1439fd98492f4d39a19299ba219c45de.r2.dev/{folder_name}"
    }
    
    # 檢查封面是否存在
    cover_file = os.path.join(folder_path, "cover.jpg")
    if not os.path.exists(cover_file):
        if verbose:
            print(f"警告：{folder_name} 資料夾中找不到 cover.jpg 檔案")
    
    try:
        # 讀取簡介資訊
        with open(intro_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 解析作者
        author_match = re.search(r'作者\s*:\s*(.*?)[\r\n]', content)
        if author_match:
            manga_info["author"] = author_match.group(1).strip()
        
        # 解析標籤
        tags_match = re.search(r'類型\s*:\s*(.*?)[\r\n]', content)
        if tags_match:
            manga_info["tags"] = [tag.strip() for tag in tags_match.group(1).strip().split(',')]
        
        # 解析韓文連結
        kr_url_match = re.search(r'韓文連結\s*:\s*(.*?)(?:[\r\n]|$)', content)
        if kr_url_match:
            manga_info["koreanUrl"] = kr_url_match.group(1).strip().replace('"', '')
        
        # 解析英文連結
        en_url_match = re.search(r'英文連結\s*:\s*(.*?)(?:[\r\n]|$)', content)
        if en_url_match:
            manga_info["englishUrl"] = en_url_match.group(1).strip().replace('"', '')
        
        # 提取描述（重寫描述提取邏輯，更精確地排除標題和連結行）
        lines = content.split('\n')
        description_lines = []
        
        # 標記連結和標題行結束的位置，從而找到描述的開始位置
        info_done = False
        for i, line in enumerate(lines):
            # 跳過標題行和空行
            if not line.strip() or line.strip().startswith('#'):
                continue
                
            # 如果找到作者、類型、韓文連結或英文連結行，標記仍在資訊部分
            if re.match(r'作者\s*:|類型\s*:|韓文連結\s*:|英文連結\s*:', line):
                info_done = False
                continue
            
            # 已經過了資訊行，開始收集描述
            if i > 0 and not info_done:
                info_done = True
                
            # 收集描述行
            if info_done:
                # 排除任何包含URL的行（防止連結殘留）
                if not re.search(r'https?://\S+', line):
                    description_lines.append(line.strip())
        
        if description_lines:
            manga_info["description"] = '\n'.join(description_lines)
        else:
            if verbose:
                print(f"警告：{folder_name} 無法解析描述")
            manga_info["description"] = ""
        
        # 獲取資料夾的最後修改時間作為最後更新時間
        manga_info["lastUpdated"] = get_folder_modified_time(folder_path)
        
        # 掃描章節資料夾
        manga_info["chapters"] = scan_chapters(folder_path, verbose)
        
        return manga_info
    
    except Exception as e:
        if verbose:
            print(f"處理資料夾 {folder_name} 時出錯：{str(e)}")
        return None

def scan_chapters(folder_path, verbose=False):
    """掃描漫畫資料夾中的章節資料夾"""
    
    chapters = []
    
    # 獲取所有數字命名的資料夾（章節）
    for item in os.listdir(folder_path):
        chapter_path = os.path.join(folder_path, item)
        if os.path.isdir(chapter_path) and item.isdigit():
            try:
                chapter_id = int(item)
                
                # 計算圖片數量（只計算jpg和png文件）
                image_count = sum(1 for f in os.listdir(chapter_path) 
                                if f.lower().endswith(('.jpg', '.jpeg', '.png')) 
                                and os.path.isfile(os.path.join(chapter_path, f)))
                
                # 獲取章節資料夾的最後修改時間
                chapter_updated = get_folder_modified_time(chapter_path)
                
                chapters.append({
                    "id": chapter_id,
                    "lastUpdated": chapter_updated,
                    "total": image_count
                })
            except Exception as e:
                if verbose:
                    print(f"處理章節 {item} 時出錯：{str(e)}")
    
    # 按章節ID排序
    chapters.sort(key=lambda x: x["id"])
    
    return chapters

def display_manga_list(manga_data=None):
    """顯示漫畫列表"""
    
    if manga_data is None:
        # 如果沒有提供數據，嘗試從JSON檔案載入
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "manga.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    manga_data = json.load(f)
            except Exception as e:
                print(f"載入 manga.json 檔案時出錯：{str(e)}")
                return
        else:
            print("找不到 manga.json 檔案。請先執行掃描命令。")
            return
    
    if not manga_data or "manga" not in manga_data or not manga_data["manga"]:
        print("漫畫列表為空。")
        return
    
    print("\n==== 漫畫列表 ====")
    print(f"共 {len(manga_data['manga'])} 部漫畫")
    print("=" * 50)
    
    for i, manga in enumerate(manga_data["manga"], 1):
        print(f"{i}. {manga['title']}")
        print(f"   作者: {manga.get('author', '未知')}")
        print(f"   標籤: {', '.join(manga.get('tags', ['未分類']))}")
        print(f"   章節: {len(manga.get('chapters', []))} 章")
        print("-" * 50)

def manga_detail(manga_index, manga_data=None):
    """顯示特定漫畫的詳細資訊"""
    
    if manga_data is None:
        # 如果沒有提供數據，嘗試從JSON檔案載入
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "manga.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    manga_data = json.load(f)
            except Exception as e:
                print(f"載入 manga.json 檔案時出錯：{str(e)}")
                return
        else:
            print("找不到 manga.json 檔案。請先執行掃描命令。")
            return
    
    if not manga_data or "manga" not in manga_data or not manga_data["manga"]:
        print("漫畫列表為空。")
        return
    
    if manga_index < 1 or manga_index > len(manga_data["manga"]):
        print(f"無效的漫畫索引。有效範圍：1 - {len(manga_data['manga'])}")
        return
    
    manga = manga_data["manga"][manga_index - 1]
    
    print("\n==== 漫畫詳細資訊 ====")
    print(f"標題: {manga['title']}")
    print(f"作者: {manga.get('author', '未知')}")
    print(f"標籤: {', '.join(manga.get('tags', ['未分類']))}")
    print(f"最後更新: {manga.get('lastUpdated', '未知')}")
    print(f"韓文連結: {manga.get('koreanUrl', '無')}")
    print(f"英文連結: {manga.get('englishUrl', '無')}")
    print(f"封面URL: {manga.get('cover', '無')}")
    print(f"R2 URL: {manga.get('r2Url', '無')}")
    
    print("\n描述:")
    print(manga.get('description', '無描述'))
    
    print("\n章節列表:")
    if not manga.get('chapters'):
        print("無章節")
    else:
        for chapter in manga["chapters"]:
            print(f"第 {chapter['id']} 章 - {chapter['total']} 頁 - 更新時間: {chapter['lastUpdated']}")

def main():
    parser = argparse.ArgumentParser(description="漫畫資訊掃描與管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # 掃描命令
    scan_parser = subparsers.add_parser("scan", help="掃描漫畫資料夾並生成JSON檔案")
    scan_parser.add_argument("-o", "--output", default="manga.json", help="輸出JSON檔案的名稱")
    scan_parser.add_argument("-v", "--verbose", action="store_true", help="顯示詳細進度訊息")
    
    # 列表命令
    list_parser = subparsers.add_parser("list", help="顯示漫畫列表")
    
    # 詳細資訊命令
    detail_parser = subparsers.add_parser("detail", help="顯示特定漫畫的詳細資訊")
    detail_parser.add_argument("index", type=int, help="漫畫索引（從1開始）")
    
    args = parser.parse_args()
    
    # 如果沒有提供命令，默認執行掃描
    if not args.command:
        print("未提供命令，默認執行掃描...")
        manga_data = scan_manga_folders(output_file="manga.json", verbose=False)
        display_manga_list(manga_data)
        return
    
    # 執行相應的命令
    if args.command == "scan":
        scan_manga_folders(output_file=args.output, verbose=args.verbose)
    
    elif args.command == "list":
        display_manga_list()
    
    elif args.command == "detail":
        manga_detail(args.index)

if __name__ == "__main__":
    main() 