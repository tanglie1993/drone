import re
from collections import defaultdict

# ================== 用户配置区域 ==================
INSTITUTION_MAPPING = {
    "Purdue University System": "Purdue University",
    "Auburn University System": "Auburn University",
    "University System of Maryland": "University of Maryland",
    "University of Maryland College Park": "University of Maryland",
    "Erasmus University Rotterdam - Excl Erasmus MC": "Erasmus University Rotterdam",
}

EXCLUDE_INSTITUTIONS = set()
OUTPUT_FILE = "institution_rankings.txt"


# ================== 数据处理函数 ==================
def clean_institution_name(raw_name):
    """机构名称标准化处理"""
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
    """解析WOS文件结构"""
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
    """解析单条记录数据"""
    data = defaultdict(list)
    current_field = None

    for line in record_lines:
        if re.match(r'^[A-Z]{1,2}\d?\s', line[:3]):
            field_code = line[:2]
            content = line[3:].strip()
            current_field = field_code
            data[field_code].append(content)
        elif current_field:
            data[current_field][-1] += ' ' + line.strip()

    # 处理机构信息
    institutions = set()
    for c3 in data.get('C3', []):
        for raw_inst in c3.split(';'):
            cleaned = clean_institution_name(raw_inst)
            if cleaned and cleaned not in EXCLUDE_INSTITUTIONS:
                institutions.add(cleaned)

    return {
        'year': int(data['PY'][0]) if data.get('PY') else 0,
        'citations': int(data['TC'][0]) if data.get('TC') else 0,
        'title': ' '.join(data.get('TI', [])),
        'abstract': ' '.join(data.get('AB', [])),
        'authors': data.get('AU', []),
        'institutions': institutions
    }


# ================== 统计计算函数 ==================
def calculate_h_index(citations):
    """计算H指数"""
    sorted_cites = sorted(citations, reverse=True)
    h = 0
    for i in range(len(sorted_cites)):
        if sorted_cites[i] >= i + 1:
            h = i + 1
        else:
            break
    return h


def generate_competitive_ranking(data, key):
    """生成竞争性排名（处理并列）"""
    sorted_items = sorted(data.items(),
                          key=lambda x: (-x[1][key], x[0]))

    rankings = []
    prev_value = None
    current_rank = 1
    position = 1

    for item in sorted_items:
        current_value = item[1][key]
        if prev_value is None:
            rankings.append((current_rank, [item]))
            prev_value = current_value
        else:
            if current_value == prev_value:
                rankings[-1][1].append(item)
            else:
                current_rank = position
                rankings.append((current_rank, [item]))
            prev_value = current_value
        position += 1

    # 合并前10名
    result = []
    total = 0
    for rank_group in rankings:
        group_size = len(rank_group[1])
        if total + group_size > 10:
            result.append((rank_group[0], rank_group[1][:10 - total]))
            break
        result.append(rank_group)
        total += group_size

    return result


# ================== 主程序 ==================
def main(file_path):
    # 数据读取
    records = parse_records(file_path)
    articles = [parse_record(r) for r in records]

    # 初始化统计存储
    stats = defaultdict(lambda: {
        'count': 0,
        'citations': [],
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
                stats[inst]['citations'].append(art['citations'])
                stats[inst]['articles'].append({
                    'title': art['title'],
                    'abstract': art['abstract'],
                    'citations': art['citations'],
                    'authors': art['authors']
                })

    # 计算H指数
    for inst in stats:
        stats[inst]['h_index'] = calculate_h_index(stats[inst]['citations'])

    # 生成排行榜
    count_ranking = generate_competitive_ranking(stats, 'count')
    hindex_ranking = generate_competitive_ranking(stats, 'h_index')

    # 输出到文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        # 输出发文量排行榜
        f.write("=== 发文量Top10机构（含并列） ===\n")
        _write_ranking_table(f, count_ranking, 'count')

        # 输出H指数排行榜
        f.write("\n\n=== H指数Top10机构（含并列） ===\n")
        _write_ranking_table(f, hindex_ranking, 'h_index')

        # 输出论文详情
        f.write("\n\n=== 高被引论文详情 ===\n")
        _write_paper_details(f, count_ranking, "发文量")
        _write_paper_details(f, hindex_ranking, "H指数")


def _write_ranking_table(f, ranking, key):
    """输出排名表格"""
    f.write("{:<5} {:<50} {:<10}\n".format("名次", "机构名称", "数量" if key == 'count' else "H指数"))
    current_rank = 1
    for rank_group in ranking:
        actual_rank = rank_group[0]
        for item in rank_group[1]:
            inst = item[0]
            value = item[1][key]
            f.write("{:<5} {:<50} {:<10}\n".format(
                f"第{actual_rank}名",
                inst,
                value
            ))
        current_rank += len(rank_group[1])


def _write_paper_details(f, ranking, title):
    """输出论文详情"""
    f.write(f"\n\n=== {title}Top10机构高被引论文 ===\n")
    for rank_group in ranking:
        rank = rank_group[0]
        for item in rank_group[1]:
            inst, data = item
            f.write(f"\n◆ {title}第{rank}名：{inst}\n")
            f.write(f"▷ 发文量：{data['count']}  H指数：{data['h_index']}\n")

            top_articles = sorted(data['articles'],
                                  key=lambda x: (-x['citations'], x['title']))[:5]

            for idx, art in enumerate(top_articles, 1):
                f.write(f"\n▣ 论文{idx} [被引：{art['citations']}次]\n")
                f.write(f"▨ 作者：{', '.join(art['authors'])}\n")
                f.write(f"▨ 标题：{art['title']}\n")
                f.write(f"▩ 摘要：{art['abstract'][:200]}...\n" if art['abstract'] else "（无摘要）\n")


if __name__ == "__main__":

    main('data/data.txt')
    print(f"分析报告已生成至: {OUTPUT_FILE}")