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
    title = re.sub(r'[ \ufffd\u0000-\u001f\u007f-\u009f]', '', title)
    
    # 檢查是否為簡介或譯名
    if '簡介' in title:
        return '簡介'
    elif '譯名' in title or title.endswith('譯名'):
        return '譯名'
    
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
    
    # 移除特定的字符串
    unwanted_strings = [
        '身為高中老師的我和學生們集體傳送到有最強排行榜的異世界，從路人角色',
        '座位時被S級美少女包圍，祕密關係就此開始。展開旅程',
        '就算轉生到了一無所知的遊戲世界我也會全力守護原作',
        '勇者的我，為了阻止自己所創立的中二病秘密結社而再',
        '線的我居然被說是廢物？算了,我要去尋找可愛老婆展開旅程'
    ]
    for s in unwanted_strings:
        title = title.replace(s, '')
    
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
    return ["異世界", "奇幻"]

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

def process_novel_directory(novel_dir, script_dir):
    try:
        print(f"\n開始處理目錄：{os.path.basename(novel_dir)}")
        print(f"處理小說目錄：{novel_dir}")
        
        # 計算相對於腳本目錄的相對路徑
        relative_novel_path = os.path.relpath(novel_dir, script_dir)
        
        # 獲取目錄中的所有markdown文件，並過濾掉不需要的文件
        files = []
        total_word_count = 0  # 添加總字數計數器
        
        for f in os.listdir(novel_dir):
            if not f.endswith('.md'):
                continue
            # 只接受以數字開頭的文件，或者是「簡介」或「譯名」
            if not (f.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')) or 
                   '簡介' in f or '譯名' in f):
                continue
            files.append(f)
            
            # 計算每個文件的字數
            file_path = os.path.join(novel_dir, f)
            try:
                # 跳過簡介和譯名檔案的字數計算
                if '簡介' not in f and '譯名' not in f:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        # 移除 markdown 標記和空白字符後計算字數
                        clean_content = re.sub(r'[#*`\n\r\s]', '', content)
                        word_count = len(clean_content)
                        total_word_count += word_count
            except Exception as e:
                print(f"計算文件 {f} 字數時發生錯誤：{e}")
            
        print(f"找到 {len(files)} 個章節文件")
        print(f"總字數：{total_word_count}")
        
        # 提取小說標題
        novel_title = os.path.basename(novel_dir).strip('《》')
        
        # 讀取簡介文件獲取標籤和作者
        intro_file = os.path.join(novel_dir, '00 簡介.md')
        tags = extract_tags_from_intro(intro_file)
        author = extract_author_from_intro(intro_file)
        
        # 如果從簡介中找不到作者，使用預設值
        if not author:
            print(f"警告：無法從簡介中找到作者資訊，使用預設值")
            author = "未知作者"
        
        # 讀取封面圖片路徑（動態偵測相對路徑）
        cover_url = f"{relative_novel_path}/cover.jpg".replace('\\', '/')
        
        # 初始化章節列表和小說最後更新時間
        chapters = []
        latest_chapter_time = datetime(1970, 1, 1)  # 初始化為最早時間
        
        # 處理每個markdown文件
        for file in sorted(files):
            file_path = os.path.join(novel_dir, file)
            
            # 獲取文件修改時間
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path))
            last_modified_str = last_modified.strftime('%Y-%m-%d %H:%M:%S')
            
            # 從文件名提取章節號
            chapter_num = extract_chapter_number(file)
            
            # 清理並格式化標題
            title = clean_title(file.replace('.md', ''))
            
            # 如果是簡介，設置id為-1.0
            if '簡介' in title:
                chapter_num = -1.0
            # 如果不是簡介章節，且時間更新，則更新小說最後更新時間
            elif '簡介' not in title and last_modified > latest_chapter_time:
                latest_chapter_time = last_modified
            
            # 構建章節路徑（動態偵測相對路徑）
            url = f"{relative_novel_path}/{file}".replace('\\', '/')
            
            # 添加章節信息
            chapter = {
                "id": chapter_num,
                "title": title,
                "url": url,
                "lastUpdated": last_modified_str
            }
            chapters.append(chapter)
        
        # 如果沒有找到有效的章節更新時間（可能所有章節都是簡介），使用目錄的修改時間
        if latest_chapter_time == datetime(1970, 1, 1):
            latest_chapter_time = datetime.fromtimestamp(os.path.getmtime(novel_dir))
            
        novel_last_modified_str = latest_chapter_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # 讀取簡介內容和原始URL
        description = ""
        original_urls = []
        if os.path.exists(intro_file):
            with open(intro_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 尋找所有原始URL
                url_matches = re.finditer(r'(https?://[^\s]+)', content)
                for match in url_matches:
                    original_urls.append(match.group(1))
                
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
        
        # 構建小說信息
        novel = {
            "title": novel_title,
            "cover": cover_url,
            "author": author,
            "tags": tags,
            "originalUrl": "、".join(original_urls),
            "description": description,
            "lastUpdated": novel_last_modified_str,
            "totalWordCount": total_word_count,  # 移到 chapters 前面
            "chapters": sorted(chapters, key=lambda x: x["id"])
        }
        
        print(f"成功處理小說：{novel_title}")
        return novel
        
    except Exception as e:
        print(f"處理目錄時發生錯誤：{e}")
        return None

def main():
    try:
        # 獲取當前目錄
        script_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"當前目錄：{script_dir}")
        
        # 掃描當前目錄下的所有小說目錄
        novels = []
        for item in os.listdir(script_dir):
            if item in ["generate_chapters.py", "novels.json", ".git", "__pycache__"]:
                continue
                
            novel_dir = os.path.join(script_dir, item)
            if os.path.isdir(novel_dir):
                print(f"\n開始處理目錄：{item}")
                novel_data = process_novel_directory(novel_dir, script_dir)
                if novel_data:
                    novels.append(novel_data)
                    print(f"成功處理小說：{novel_data['title']}")
                else:
                    print(f"跳過目錄：{item}")
        
        # 將結果寫入當前目錄的 novels.json
        output_file = os.path.join(script_dir, 'novels.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"novels": novels}, f, ensure_ascii=False, indent=2)
        
        print(f"\n成功處理了 {len(novels)} 本小說的資料")
        print(f"輸出文件位置：{output_file}")
    except Exception as e:
        print(f"執行腳本時出錯：{str(e)}")

if __name__ == "__main__":
    main()
