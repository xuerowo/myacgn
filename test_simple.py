#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

# 測試簡單的 Git 狀態解析
result = subprocess.run(
    ["git", "status", "--porcelain"],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    encoding='utf-8',
    errors='ignore'
)

print("Git 狀態原始輸出:")
for i, line in enumerate(result.stdout.strip().split('\n')):
    print(f"行 {i}: '{line}'")
    if len(line) >= 3:
        status = line[:2]
        filename = line[3:]
        print(f"  狀態: '{status}'")
        print(f"  檔名: '{filename}' (長度: {len(filename)})")
        print(f"  檔名字節: {filename.encode('utf-8')}")
    print()