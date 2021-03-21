from collections import defaultdict, Counter
import re

# 读取文件
with open('data/data.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 统计文章标题被引次数
title_citation_count = defaultdict(int)
current_title = ""
current_citations = 0
is_title = False  # 标记是否正在读取标题

# 正则表达式匹配两个大写字母和一个空格或制表符开头的行
field_pattern = re.compile(r'^[A-Z]{2}[ \t]')

for line in lines:
    # 如果行以 TI 开头，开始读取标题
    if line.startswith('TI'):
        is_title = True
        current_title = line.strip().split('TI ')[-1]  # 提取标题的第一部分
    # 如果行以 TC 开头，提取被引次数
    elif line.startswith('TC'):
        current_citations = int(line.split()[-1])
        # 将被引次数分配给当前文章标题
        title_citation_count[current_title] += current_citations
    # 如果正在读取标题，并且当前行不是新字段的开头，则拼接标题
    elif is_title and not field_pattern.match(line):
        current_title += " " + line.strip()
    # 如果当前行是新字段的开头，则停止读取标题
    elif field_pattern.match(line):
        is_title = False

# 获取高频被引文章标题（例如前10个）
top_titles = Counter(title_citation_count).most_common(10)

# 输出高频被引文章标题
print("高频被引文章标题统计：")
for title, citations in top_titles:
    print(f"{title}: {citations} 次")