import os
import json
from datetime import datetime
import re

def extract_chapter_number(filename):
    # 先嘗試匹配「第x話」格式
    match = re.search(r'第(\d+(?:\.\d+)?)話', filename)
    if match:
        return float(match.group(1))
    
    # 再嘗試從文件名開頭提取數字（包括小數）
    match = re.match(r'^(\d+(?:\.\d+)?)', filename)
    if match:
        return float(match.group(1))
    
    # 最後嘗試匹配帶有「・」的數字格式
    match = re.search(r'(\d+)・(\d+)', filename)
    if match:
        return float(f"{match.group(1)}.{match.group(2)}")
        
    return 0.0  # 確保返回浮點數

def clean_title(title):
    # 移除特殊字符和控制字符
    title = re.sub(r'[�\ufffd\u0000-\u001f\u007f-\u009f]', '', title)
    
    # 檢查是否為簡介
    if '簡介' in title:
        return '簡介'
    
    # 提取章節號和標題
    chapter_num = extract_chapter_number(title)
    
    # 移除章節號和多餘的空格
    title = re.sub(r'^(\d+(?:\.\d+)?)\s*', '', title)
    title = re.sub(r'第\d+(?:\.\d+)?話\s*', '', title)
    title = re.sub(r'\d+・\d+\s*', '', title)
    
    # 移除方括號及其內容
    title = re.sub(r'\[.*?\]', '', title)
    
    # 移除特定的後綴文本
    title = re.sub(r'～.*?～', '', title)
    title = re.sub(r'《.*?》', '', title)
    
    # 移除多餘的空格
    title = ' '.join(title.split())
    
    # 格式化為「第x話 xxx」格式
    if title:
        # 如果章節號是整數，不顯示小數點
        if chapter_num.is_integer():
            title = f"第{int(chapter_num)}話 {title.strip()}"
        else:
            title = f"第{chapter_num}話 {title.strip()}"
    else:
        if chapter_num.is_integer():
            title = f"第{int(chapter_num)}話"
        else:
            title = f"第{chapter_num}話"
        
    return title

def extract_tags_from_intro(intro_path):
    try:
        with open(intro_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 尋找類型標籤
        match = re.search(r'類型[：:]\s*([^\n]+)', content)
        if match:
            # 分割並清理標籤
            tags = [tag.strip() for tag in re.split(r'[,，、/]', match.group(1))]
            # 移除空標籤
            tags = [tag for tag in tags if tag]
            return tags
    except Exception as e:
        print(f"無法讀取或解析簡介文件：{e}")
    
    # 如果沒有找到標籤，返回預設標籤
    return ["網漫"]

def extract_author_from_intro(intro_path):
    try:
        with open(intro_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 嘗試匹配作者資訊
        # 匹配模式：作者：xxx 或 作者:xxx
        author_match = re.search(r'作者[：:]\s*([^\n]+)', content)
        if author_match:
            author = author_match.group(1).strip()
            return author
            
        # 如果找不到作者資訊，返回空字串
        return ""
    except Exception as e:
        print(f"無法讀取或解析簡介文件中的作者資訊：{e}")
        return ""

def process_manga_directory(manga_dir):
    try:
        print(f"\n開始處理目錄：{os.path.basename(manga_dir)}")
        print(f"處理網漫目錄：{manga_dir}")
        
        # 獲取目錄中的所有圖片目錄
        chapters = []
        chapter_dirs = []
        
        for item in os.listdir(manga_dir):
            if item in ['簡介.md', 'cover.jpg']:
                continue
            
            chapter_path = os.path.join(manga_dir, item)
            if os.path.isdir(chapter_path):
                chapter_dirs.append(item)
        
        print(f"找到 {len(chapter_dirs)} 個章節目錄")
        
        # 提取網漫標題
        manga_title = os.path.basename(manga_dir)
        
        # 讀取簡介文件獲取標籤和作者
        intro_file = os.path.join(manga_dir, '簡介.md')
        tags = extract_tags_from_intro(intro_file)
        author = extract_author_from_intro(intro_file)
        
        # 如果從簡介中找不到作者，使用預設值
        if not author:
            print(f"警告：無法從簡介中找到作者資訊，使用預設值")
            author = "未知作者"
        
        # 讀取封面圖片URL
        cover_url = f"https://raw.githubusercontent.com/xuerowo/myacg/main/網漫翻譯/{manga_title}/cover.jpg"
        
        # 獲取網漫目錄的最後修改時間
        manga_last_modified = datetime.fromtimestamp(os.path.getmtime(manga_dir))
        manga_last_modified_str = manga_last_modified.strftime('%Y-%m-%d %H:%M:%S')
        
        # 處理每個章節目錄
        for chapter_dir in sorted(chapter_dirs):
            dir_path = os.path.join(manga_dir, chapter_dir)
            
            # 獲取目錄修改時間
            last_modified = datetime.fromtimestamp(os.path.getmtime(dir_path))
            last_modified_str = last_modified.strftime('%Y-%m-%d %H:%M:%S')
            
            # 從目錄名提取章節號
            chapter_id = int(extract_chapter_number(chapter_dir))
            
            # 計算目錄中的圖片總數
            image_count = len([f for f in os.listdir(dir_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))])
            
            # 添加章節信息
            chapter = {
                "id": chapter_id,
                "lastUpdated": last_modified_str,
                "total": image_count
            }
            chapters.append(chapter)
        
        # 讀取簡介內容和原始URL
        description = ""
        korean_urls = []
        english_urls = []
        if os.path.exists(intro_file):
            with open(intro_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # 尋找韓文和英文URL區段
                korean_section = re.search(r'韓文正版連結[：:](.*?)(?=英文正版連結[：:]|$)', content, re.DOTALL)
                english_section = re.search(r'英文正版連結[：:](.*?)(?=\n\n|$)', content, re.DOTALL)
                
                # 提取韓文URL
                if korean_section:
                    korean_urls = [url.strip() for url in re.findall(r'(https?://[^\s]+)', korean_section.group(1))]
                
                # 提取英文URL
                if english_section:
                    english_urls = [url.strip() for url in re.findall(r'(https?://[^\s]+)', english_section.group(1))]
                
                # 找到最後一個URL之後的內容作為描述
                lines = content.split('\n')
                last_url_index = -1
                for i, line in enumerate(lines):
                    if 'http' in line:
                        last_url_index = i
                if last_url_index != -1:
                    description = '\n'.join(lines[last_url_index + 2:])
                    # 如果描述為空，使用整個內容
                    if not description.strip():
                        description = content
                else:
                    description = content
        
        # 構建網漫信息
        manga = {
            "title": manga_title,
            "cover": cover_url,
            "r2Url": f"https://pub-1439fd98492f4d39a19299ba219c45de.r2.dev/{manga_title}",
            "author": author,
            "tags": tags,
            "koreanUrl": "、".join(korean_urls) if korean_urls else "",
            "englishUrl": "、".join(english_urls) if english_urls else "",
            "description": description,
            "lastUpdated": manga_last_modified_str,
            "chapters": sorted(chapters, key=lambda x: x["id"])
        }
        
        print(f"成功處理網漫：{manga_title}")
        return manga
        
    except Exception as e:
        print(f"處理目錄時發生錯誤：{e}")
        return None

def main():
    try:
        # 獲取當前目錄
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"當前目錄：{script_dir}")
        
        # 掃描當前目錄下的所有網漫目錄
        manga_list = []
        for item in os.listdir(script_dir):
            if item in ["generate_manga.py", "manga.json", ".git", "__pycache__"]:
                continue
                
            manga_dir = os.path.join(script_dir, item)
            if os.path.isdir(manga_dir):
                print(f"\n開始處理目錄：{item}")
                manga_data = process_manga_directory(manga_dir)
                if manga_data:
                    manga_list.append(manga_data)
                    print(f"成功處理網漫：{manga_data['title']}")
                else:
                    print(f"跳過目錄：{item}")
        
        # 將結果寫入當前目錄的 manga.json
        output_file = os.path.join(script_dir, 'manga.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"manga": manga_list}, f, ensure_ascii=False, indent=2)
        
        print(f"\n成功處理了 {len(manga_list)} 本網漫的資料")
        print(f"輸出文件位置：{output_file}")
    except Exception as e:
        print(f"執行腳本時出錯：{str(e)}")

if __name__ == "__main__":
    main() 