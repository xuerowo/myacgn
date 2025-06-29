import os
import glob
import re

def replace_in_files():
    # 獲取當前目錄下所有.md檔案
    md_files = glob.glob('*.md')
    
    for file_path in md_files:
        # 替換檔案內容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # 檢查內容中是否有"放逐"
        if '放逐' in content:
            new_content = content.replace('放逐', '流放')
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f'已將檔案 {file_path} 中的內容 "放逐" 替換為 "流放"')
        
        # 替換檔案名稱
        if '放逐' in file_path:
            new_file_path = file_path.replace('放逐', '流放')
            os.rename(file_path, new_file_path)
            print(f'已將檔案名稱從 {file_path} 改為 {new_file_path}')

if __name__ == "__main__":
    print('開始替換所有 .md 檔案中的 "放逐" 為 "流放"...')
    replace_in_files()
    print('替換完成！') 