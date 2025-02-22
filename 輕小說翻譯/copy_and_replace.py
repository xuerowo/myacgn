import os
import shutil
import re

def copy_and_replace_files(source_novel, target_novels):
    source_dir = os.path.join(os.path.dirname(__file__), source_novel)
    source_files = ['noveldetail.html', 'reader.html']
    
    # 確保源文件存在
    for file in source_files:
        source_file = os.path.join(source_dir, file)
        if not os.path.exists(source_file):
            print(f"錯誤：源文件 {file} 不存在於 {source_novel}")
            return

    # 處理每個目標小說資料夾
    for novel_dir in target_novels:
        if novel_dir == source_novel:  # 跳過源資料夾
            continue
            
        print(f"\n處理資料夾：{novel_dir}")
        target_dir = os.path.join(os.path.dirname(__file__), novel_dir)
        
        # 從資料夾名稱中提取小說標題（在《》之間的文字）
        target_novel_name = re.search(r'《(.+?)》', novel_dir)
        if not target_novel_name:
            print(f"警告：無法從資料夾名稱中提取小說標題：{novel_dir}")
            continue
        target_novel_name = target_novel_name.group(1)
        
        # 提取源小說名稱
        source_novel_name = re.search(r'《(.+?)》', source_novel).group(1)
        
        # 複製並替換每個文件
        for file in source_files:
            source_file = os.path.join(source_dir, file)
            target_file = os.path.join(target_dir, file)
            
            # 讀取源文件
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替換小說標題
            new_content = content.replace(source_novel_name, target_novel_name)
            
            # 寫入目標文件
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"已複製並更新：{file}")

def main():
    # 源小說資料夾
    source_novel = '《無知轉生 ～就算轉生到了一無所知的遊戲世界我也會全力守護原作～》'
    
    # 獲取所有小說資料夾
    current_dir = os.path.dirname(__file__)
    novel_dirs = [d for d in os.listdir(current_dir) 
                 if os.path.isdir(os.path.join(current_dir, d)) 
                 and d.startswith('《') and d.endswith('》')]
    
    print(f"開始處理文件...")
    copy_and_replace_files(source_novel, novel_dirs)
    print("\n完成！")

if __name__ == '__main__':
    main()
