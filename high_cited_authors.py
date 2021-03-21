from collections import defaultdict, Counter

# 读取文件
with open('data/data.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 统计作者被引次数
author_citation_count = defaultdict(int)
current_authors = []
current_citations = 0

for line in lines:
    if line.startswith('AU'):
        # 提取作者行，并拆分为单个作者
        current_authors = [author.strip() for author in line.split('AU ')[-1].split('; ')]
    elif line.startswith('TC'):
        # 提取被引次数
        current_citations = int(line.split()[-1])
        # 将被引次数分配给当前作者
        for author in current_authors:
            author_citation_count[author] += current_citations

# 获取高频被引作者（例如前10个）
top_authors = Counter(author_citation_count).most_common(10)

# 输出高频被引作者
print("高频被引作者统计：")
for author, citations in top_authors:
    print(f"{author}: {citations} 次")