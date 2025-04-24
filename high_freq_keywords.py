from collections import defaultdict, Counter

# 手工填入同义词映射表
# 格式：标准词: [同义词1, 同义词2, ...]
synonyms = {
    "Unmanned aerial vehicle": ["uav", "uavs", "unmanned aerial vehicles",
                                "unmanned aerial vehicles (uav)", "unmanned aerial vehicle (uav)", "uas",
                                "unmanned aerial vehicle", "autonomous aerial vehicles"],
    "drone": ["Drone", "drones"],
    "Traveling salesman problem": ["tsp", "traveling salesperson problem"],
    "Vehicle routing problem": ["vrp", "vehicle route problem"],
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

# 统计关键词
keyword_count = defaultdict(int)

for line in lines:
    if line.startswith('DE'):
        # 提取关键词行，并拆分为单个关键词
        keywords = line.strip().split('DE ')[-1].split('; ')
        for keyword in keywords:
            # 格式化关键词：首字母大写，其余小写
            formatted_keyword = keyword.strip().capitalize()
            # 处理同义词：如果关键词在同义词映射表中，则替换为标准形式
            standardized_keyword = synonym_to_standard.get(formatted_keyword.lower(), formatted_keyword)
            keyword_count[standardized_keyword] += 1

# 获取高频关键词（例如前10个）
top_keywords = Counter(keyword_count).most_common(50)

# 输出高频关键词
print("高频关键词统计：")
for keyword, count in top_keywords:
    print(f"{keyword}: {count} 次")