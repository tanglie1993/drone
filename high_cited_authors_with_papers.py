import re
from collections import defaultdict

# 定义正则表达式匹配字段标识符
field_pattern = re.compile(r'^([A-Z]{2})\s*(.*)')  # 允许字段代码前有空格（处理后）

articles = []
current_article = None
current_field = None

with open('data/data.txt', 'r', encoding='utf-8') as file:
    for line in file:
        # 清除特殊字符和格式
        line = line.encode('utf-8').replace(b'\xef\xbb\xbf', b'').decode('utf-8')  # 处理BOM
        line = line.lstrip('\ufeff')  # 去除零宽度非断开空格
        line = line.rstrip('\n')  # 去除换行符

        # 检测新文章开始（PT J）
        if line.startswith('PT J'):
            if current_article:
                articles.append(current_article)
            current_article = {
                'authors': [],
                'title': '',
                'abstract': '',
                'citations': 0
            }
            current_field = None
            continue

        # 解析字段内容（增强鲁棒性）
        if len(line) >= 2:
            # 处理带缩进的续行（如作者/标题/摘要多行情况）
            if current_field and (line.startswith('   ') or not line.strip()):
                content = line.strip()
                if current_field == 'AU':
                    current_article['authors'].append(content)
                elif current_field == 'TI':
                    current_article['title'] += ' ' + content
                elif current_field == 'AB':
                    current_article['abstract'] += ' ' + content
                continue

            # 处理新字段
            match = field_pattern.match(line)
            if match:
                field_code, content = match.groups()
                current_field = field_code
                content = content.strip()

                if field_code == 'AU':
                    current_article['authors'].append(content)
                elif field_code == 'TI':
                    current_article['title'] = content
                elif field_code == 'AB':
                    current_article['abstract'] = content
                elif field_code == 'TC':
                    current_article['citations'] = int(content)

    # 添加最后一篇文章
    if current_article:
        articles.append(current_article)

import re
from collections import defaultdict

# ... [前面的解析代码保持不变，直到构建作者数据库] ...

# 构建作者数据库（添加引用次数存储）
author_db = defaultdict(lambda: {'total_citations': 0, 'publications': []})
for article in articles:
    for author in article['authors']:
        author_entry = author_db[author]
        author_entry['total_citations'] += article['citations']
        author_entry['publications'].append({
            'title': article['title'],
            'abstract': article['abstract'],
            'citations': article['citations']  # 添加单篇引用次数
        })

# 获取前10高被引作者
top_authors = sorted(author_db.items(), key=lambda x: -x[1]['total_citations'])[:12]

# 输出结果
print("高频被引作者及著作详情：")
for author, data in top_authors:
    print(f"\n=== 作者: {author} ===")
    print(f"总被引次数: {data['total_citations']}")
    print("相关文章（按单篇被引排序）:")

    # 按单篇被引降序排序
    sorted_pubs = sorted(data['publications'], key=lambda x: -x['citations'])

    for idx, pub in enumerate(sorted_pubs, 1):
        print(f"\n论文 {idx}:")
        print(f"标题: {pub['title']}")
        print(f"单篇被引: {pub['citations']}")  # 显示单篇引用次数
        print(f"摘要: {pub['abstract']}")