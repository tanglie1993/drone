from collections import defaultdict, Counter

# 手工填入同义词映射表
# 格式：标准词: [同义词1, 同义词2, ...]
synonyms = {
    "Unmanned aerial vehicle": ["uav", "drone", "drones", "uavs", "unmanned aerial vehicles",
                                "unmanned aerial vehicles (uav)", "unmanned aerial vehicle (uav)", "uas",
                                "unmanned aerial vehicle", "autonomous aerial vehicles"],
    "Traveling salesman problem": ["tsp", "traveling salesperson problem"],
    "Delivery": ["Drone delivery"],
    "Vehicle routing problem": ["vrp", "vehicle route problem", "Vehicle routing"],
    "Optimization": ["optimisation", "optimalization"],  # 英式和美式拼写
    # 在这里添加更多同义词
}

# 反转同义词映射表，方便查找
# 格式：同义词: 标准词
synonym_to_standard = {}
for standard_word, synonym_list in synonyms.items():
    for synonym in synonym_list:
        synonym_to_standard[synonym.lower()] = standard_word

# 读取文件
with open('data/data.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 初始化统计变量
keyword_count_before_2015 = defaultdict(int)  # 2015 年前的关键词统计
keyword_count_after_2015 = defaultdict(int)  # 2015 年后的关键词统计
current_year = None  # 当前文献的出版年份

for line in lines:
    # 提取出版年份
    if line.startswith('PY'):
        current_year = int(line.strip().split()[-1])  # 提取 PY 字段的年份
    # 提取关键词
    elif line.startswith('DE'):
        # 提取关键词行，并拆分为单个关键词
        keywords = line.strip().split('DE ')[-1].split('; ')
        for keyword in keywords:
            # 格式化关键词：首字母大写，其余小写
            formatted_keyword = keyword.strip().capitalize()
            # 处理同义词：如果关键词在同义词映射表中，则替换为标准形式
            standardized_keyword = synonym_to_standard.get(formatted_keyword.lower(), formatted_keyword)
            # 根据年份统计关键词
            if current_year is not None:
                if current_year < 2021:
                    keyword_count_before_2015[standardized_keyword] += 1
                else:
                    keyword_count_after_2015[standardized_keyword] += 1

# 获取高频关键词（例如前20个）
top_keywords_before_2015 = Counter(keyword_count_before_2015).most_common(15)
top_keywords_after_2015 = Counter(keyword_count_after_2015).most_common(15)

print("2020 年前高频关键词统计：")
for keyword, count in top_keywords_before_2015:
    print(f"{keyword}: {count} 次")

print("\n2021 年后高频关键词统计：")
for keyword, count in top_keywords_after_2015:
    print(f"{keyword}: {count} 次")