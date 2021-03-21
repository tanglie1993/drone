from collections import defaultdict, Counter
import re

# 读取文件
with open('data/data.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 统计国家和被引国家
country_count = defaultdict(int)  # 国家出现次数
country_citation_count = defaultdict(int)  # 国家被引次数
country_citation_list = defaultdict(list)  # 存储每个国家的被引次数列表（用于计算 H 指数）
current_countries = []
current_citations = 0
is_c1 = False  # 标记是否正在读取 C1 字段
current_c1_lines = []  # 存储当前 C1 字段的多行内容

# 正则表达式匹配两个大写字母和一个空格或制表符开头的行
field_pattern = re.compile(r'^[A-Z]{2}[ \t]')
# 正则表达式匹配一个字母和一个数字开头的行（如 C2）
c2_pattern = re.compile(r'^[A-Z][0-9]')

# 提取国家的函数
def extract_country(address):
    # 去掉最后的句号
    address = address.rstrip('.')
    # 提取最后一段
    last_part = address.split(',')[-1].strip()
    # 如果最后一段包含 USA，则单独提取 USA
    if 'USA' in last_part:
        return 'USA'
    return last_part

# 计算 H 指数的函数
def calculate_h_index(citation_list):
    # 将被引次数从高到低排序
    sorted_citations = sorted(citation_list, reverse=True)
    # 计算 H 指数
    h_index = 0
    for i, citations in enumerate(sorted_citations):
        if citations >= i + 1:
            h_index = i + 1
        else:
            break
    return h_index

for line in lines:
    # 如果行以 C1 开头，开始读取 C1 字段
    if line.startswith('C1'):
        is_c1 = True
        current_c1_lines = [line.strip().split('C1 ')[-1]]  # 提取 C1 的第一部分
    # 如果正在读取 C1 字段，并且当前行不是新字段的开头，则拼接内容
    elif is_c1 and not field_pattern.match(line) and not c2_pattern.match(line):
        current_c1_lines.append(line.strip())
    # 如果当前行是新字段的开头（如 AU、TC、C2 等），则停止读取 C1 字段
    elif field_pattern.match(line) or c2_pattern.match(line):
        if is_c1:
            # 拼接完整的 C1 字段内容
            full_c1 = ' '.join(current_c1_lines)
            # 提取国家
            addresses = full_c1.split('; ')
            current_countries = list(dict.fromkeys([extract_country(addr) for addr in current_c1_lines]))
            is_c1 = False
    # 如果行以 TC 开头，提取被引次数
    if line.startswith('TC'):
        current_citations = int(line.split()[-1])
        # 统计国家出现次数和被引次数
        for country in current_countries:
            country_count[country] += 1
            country_citation_count[country] += current_citations
            # 记录每个国家的被引次数（用于计算 H 指数）
            country_citation_list[country].append(current_citations)

# 获取高频国家（例如前10个）
top_countries = Counter(country_count).most_common(10)
# 获取高频被引国家（例如前10个）
top_cited_countries = Counter(country_citation_count).most_common(10)
# 计算每个国家的 H 指数
country_h_index = {country: calculate_h_index(citation_list) for country, citation_list in country_citation_list.items()}
# 获取 H 指数最高的国家（例如前10个）
top_h_index_countries = sorted(country_h_index.items(), key=lambda x: x[1], reverse=True)[:10]

# 输出高频国家
print("高频国家统计：")
for country, count in top_countries:
    print(f"{country}: {count} 次")

# 输出高频被引国家
print("\n高频被引国家统计：")
for country, citations in top_cited_countries:
    print(f"{country}: {citations} 次")

# 输出 H 指数最高的国家
print("\nH 指数最高的国家统计：")
for country, h_index in top_h_index_countries:
    print(f"{country}: H 指数 {h_index}")