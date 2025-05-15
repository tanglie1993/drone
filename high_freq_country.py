import json
import re
from collections import defaultdict

import re


def extract_country_v2(address_line):
    """增强版国家提取函数"""
    # 移除作者信息
    if '] ' in address_line:
        _, address_part = address_line.split('] ', 1)
    else:
        address_part = address_line

    # 处理美国地址的特殊情况
    usa_match = re.search(r',\s*([^,]*USA)\s*\.?$', address_part, re.IGNORECASE)
    if usa_match:
        return 'USA'

    # 通用处理逻辑
    parts = [p.strip() for p in address_part.split(',')]
    for part in reversed(parts):
        clean_part = part.rstrip('.').strip()
        if clean_part:
            return clean_part
    return "Unknown"


def process_countries_v2(c1_data):
    """处理多行C1数据"""
    countries = set()

    # 统一处理为列表
    entries = c1_data if isinstance(c1_data, list) else [c1_data]

    for entry in entries:
        # 按换行符分割地址行
        for address_line in entry.split('\n'):
            line = address_line.strip()
            if not line:
                continue
            try:
                country = extract_country_v2(line)
                countries.add(country)
            except:
                continue
    return list(countries)


# 集成到主处理流程
def analyze_data(input_file):
    stats = defaultdict(lambda: {
        'count': 0,
        'total_citations': 0,
        'citations': []
    })

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line)
                tc = int(record.get('TC', 0)) if record.get('TC') else 0

                if 'C1' in record:
                    countries = process_countries_v2(record['C1'])
                    for country in countries:
                        stats[country]['count'] += 1
                        stats[country]['total_citations'] += tc
                        stats[country]['citations'].append(tc)
            except:
                continue

    # 后续计算逻辑保持不变...

def calculate_h_index(citations):
    sorted_citations = sorted(citations, reverse=True)
    h = 0
    for i, c in enumerate(sorted_citations, 1):
        if c >= i:
            h = i
        else:
            break
    return h


# 集成到主处理流程
def analyze_data(input_file):
    stats = defaultdict(lambda: {
        'count': 0,
        'total_citations': 0,
        'citations': []
    })

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line)
                tc = int(record.get('TC', 0)) if record.get('TC') else 0

                if 'C1' in record:
                    countries = process_countries_v2(record['C1'])
                    for country in countries:
                        stats[country]['count'] += 1
                        stats[country]['total_citations'] += tc
                        stats[country]['citations'].append(tc)
            except:
                continue

    # 计算最终结果
    results = []
    for country, data in stats.items():
        results.append({
            'country': country,
            'count': data['count'],
            'total_citations': data['total_citations'],
            'h_index': calculate_h_index(data['citations'])
        })

    # 按H指数排序
    return sorted(results, key=lambda x: (-x['h_index'], -x['total_citations']))[:10]


# 示例输出
if __name__ == "__main__":
    top_countries = analyze_data("data/data.jsonl")

    print("\n{:<20} {:<10} {:<15} {:<10}".format("Country", "Publications", "Total Citations", "H-index"))
    print("=" * 55)
    for item in top_countries:
        print("{:<20} {:<10} {:<15} {:<10}".format(
            item['country'],
            item['count'],
            item['total_citations'],
            item['h_index']
        ))