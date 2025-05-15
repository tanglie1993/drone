import re
from collections import defaultdict

# ================== 用户配置区域 ==================
# 机构名称标准化映射表（旧名称 -> 新名称）
INSTITUTION_MAPPING = {
    "Purdue University System": "Purdue University",
    "Auburn University System": "Auburn University",
    "University of Maryland College Park": "University of Maryland",
    "Erasmus University Rotterdam - Excl Erasmus MC": "Erasmus University Rotterdam",
    # 示例格式："旧名称": "标准名称"
}

# 需要完全排除的机构列表（全大写）
EXCLUDE_INSTITUTIONS = {
    # 示例："OBSOLETE INSTITUTION"
}


# ================== 数据处理函数 ==================
def clean_institution_name(raw_name):
    """机构名称清洗"""
    name = raw_name.strip()

    # 应用名称映射
    for old, new in INSTITUTION_MAPPING.items():
        if name.lower() == old.lower():
            return new

    # 去除系统后缀
    name = re.sub(r',.*?(System|Campus)\b', '', name, flags=re.IGNORECASE)

    # 统一缩写
    name = re.sub(r'\bUniv\b', 'University', name, flags=re.IGNORECASE)

    return name


def parse_records(file_path):
    """解析WOS文件"""
    records = []
    current_record = []
    in_record = False

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip('\n')

            if re.match(r'^PT\s', line):
                if in_record:
                    records.append(current_record)
                current_record = [line]
                in_record = True
            elif in_record and line == 'ER':
                current_record.append(line)
                records.append(current_record)
                current_record = []
                in_record = False
            elif in_record:
                current_record.append(line)

    return records


def parse_record(record_lines):
    """解析单条记录"""
    data = defaultdict(list)
    current_field = None

    for line in record_lines:
        # 检测字段开始
        if re.match(r'^[A-Z]{1,2}\d?\s', line[:3]):
            field_code = line[:2]
            content = line[3:].strip()
            current_field = field_code
            data[field_code].append(content)
        else:
            # 处理续行内容
            if current_field:
                stripped = line.strip()
                if current_field == 'AU':
                    # 每个续行视为新作者
                    data[current_field].append(stripped)
                else:
                    # 合并到当前字段
                    if data[current_field]:
                        data[current_field][-1] += ' ' + stripped

    # 处理机构信息
    institutions = set()
    for c3 in data.get('C3', []):
        for raw_inst in c3.split(';'):
            cleaned = clean_institution_name(raw_inst)
            if cleaned and cleaned not in EXCLUDE_INSTITUTIONS:
                institutions.add(cleaned)

    return {
        'year': int(data['PY'][0]) if data.get('PY') and data['PY'][0].isdigit() else 0,
        'citations': int(data['TC'][0]) if data.get('TC') and data['TC'][0].isdigit() else 0,
        'title': ' '.join(data.get('TI', [])),
        'abstract': ' '.join(data.get('AB', [])),
        'authors': data.get('AU', []),
        'institutions': institutions
    }


# ================== 统计计算函数 ==================
def calculate_h_index(citations):
    """计算H指数"""
    return sum(1 for i, v in enumerate(sorted(citations, reverse=True), 1) if v >= i)


# ================== 主程序 ==================
def main(file_path):
    # 数据读取
    records = parse_records(file_path)
    articles = [parse_record(r) for r in records]

    # 初始化统计
    stats = defaultdict(lambda: {
        'count': 0,
        'citations': 0,
        'articles': [],
        'h_index': 0
    })

    # 处理每篇文章
    for art in articles:
        if art['year'] < 2000:
            continue

        for inst in art['institutions']:
            stats[inst]['count'] += 1
            if art['citations'] > 0:
                stats[inst]['citations'] += art['citations']
                stats[inst]['articles'].append({
                    'title': art['title'],
                    'abstract': art['abstract'],
                    'citations': art['citations'],
                    'authors': art['authors']
                })

    # 计算H指数
    for inst in stats:
        citations = [a['citations'] for a in stats[inst]['articles']]
        stats[inst]['h_index'] = calculate_h_index(citations)

    # 生成排行榜
    def get_top(data, key, n=10):
        return sorted(data.items(), key=lambda x: (-x[1][key], x[0]))[:n]

    top_cited = get_top(stats, 'citations')

    # 输出排行榜
    print("=== 总被引次数Top10机构 ===")
    for rank, (inst, data) in enumerate(top_cited, 1):
        print(f"{rank:2d}. {inst:<50} {data['citations']}次")

    # 输出每个机构的TOP5论文
    print("\n=== 各机构高被引论文 ===")
    for inst, data in top_cited:
        print(f"\n◆ 机构：{inst}")
        print(f"▷ 总被引：{data['citations']}次  H-index：{data['h_index']}")

        top_articles = sorted(data['articles'],
                              key=lambda x: (-x['citations'], x['title']))[:8]

        for idx, art in enumerate(top_articles, 1):
            print(f"\n▣ 论文{idx} [被引：{art['citations']}次]")
            print(f"▨ 作者：{', '.join(art['authors'])}")
            print(f"▨ 标题：{art['title']}")
            print(f"▩ 摘要：{art['abstract']}" if art['abstract'] else "（无摘要）")


if __name__ == "__main__":
    main('data/data.txt')