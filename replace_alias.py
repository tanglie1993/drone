from collections import defaultdict

import re

# 读取同义词文件，构建同义词映射表
synonym_map = defaultdict(list)
with open('data/thesaurus.txt', 'r', encoding='utf-8') as file:
    next(file)  # 跳过表头
    for line in file:
        replace_by, label = line.strip().split('\t')
        synonym_map[replace_by.lower()].append(label.lower())

# 读取原始数据文件
with open('data/data.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 替换同义词并写入新文件
with open('data/download_modified.txt', 'w', encoding='utf-8') as output_file:
    for line in lines:
        # 遍历同义词映射表，替换同义词
        for replace_by, labels in synonym_map.items():
            for label in labels:
                # 不区分大小写替换
                line = re.sub(r'\b' + re.escape(label) + r'\b', replace_by, line, flags=re.IGNORECASE)
        # 写入新文件
        output_file.write(line)