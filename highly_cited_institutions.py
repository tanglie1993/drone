import re
import json
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


def process_c3_institutions(c3_data):
    """处理C3字段并确保单记录内机构去重"""
    raw_str = ';'.join(c3_data) if isinstance(c3_data, list) else c3_data
    processed_str = raw_str.replace('\n', ' ')

    seen = set()  # 单记录去重集合
    institutions = []

    for raw_inst in processed_str.split(';'):
        inst = raw_inst.strip()
        if not inst:
            continue

        # 关键步骤：先应用映射表再去重
        mapped_inst = INSTITUTION_MAPPING.get(inst, inst)

        if mapped_inst not in EXCLUDE_INSTITUTIONS and mapped_inst not in seen:
            seen.add(mapped_inst)
            institutions.append(mapped_inst)

    return institutions

def print_specific_columns(data, columns, title):
    """通用打印函数，指定显示的列"""
    column_titles = {
        'publications': ('Publications', 12),
        'total_citations': ('Total Citations', 15),
        'h_index': ('H-index', 10)
    }

    # 生成表头
    header = "{:<60}".format("Institution")
    for col in columns:
        title_part = column_titles[col][0]
        width = column_titles[col][1]
        header += " {:<{}}".format(title_part, width)

    print(f"\n{'=' * 30} {title} {'=' * 30}")
    print(header)
    print("-" * (60 + sum(
        [ct[1] + 1 for ct in column_titles.values() if ct[0] in [column_titles[c][0] for c in columns]])))

    # 打印数据行
    for item in data:
        line = "{:<60}".format(item['institution'])
        for col in columns:
            width = column_titles[col][1]
            line += " {:<{}}".format(item[col], width)
        print(line)



def calculate_h_index(citations):
    sorted_citations = sorted(citations, reverse=True)
    h = 0
    for i, c in enumerate(sorted_citations, 1):
        if c >= i:
            h = i
        else:
            break
    return h


def analyze_c3_institutions(input_file):
    """精确统计机构参与情况"""
    stats = defaultdict(lambda: {
        'publications': 0,  # 参与论文数（已去重）
        'total_citations': 0,
        'citations': []  # 每篇论文贡献的被引次数
    })

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                record = json.loads(line)
                tc = int(record.get('TC', 0)) or 0

                if 'C3' in record:
                    unique_insts = process_c3_institutions(record['C3'])
                    for inst in unique_insts:
                        stats[inst]['publications'] += 1
                        stats[inst]['total_citations'] += tc
                        stats[inst]['citations'].append(tc)
            except Exception as e:
                print(f"处理异常记录: {e}")
                continue

    # 计算H指数
    results = []
    for inst, data in stats.items():
        results.append({
            'institution': inst,
            'publications': data['publications'],
            'total_citations': data['total_citations'],
            'h_index': calculate_h_index(data['citations'])
        })

    return results


def generate_top_lists(results):
    """生成三个Top10排行榜"""
    # 按总被引排序
    top_citations = sorted(results,
                           key=lambda x: (-x['total_citations'], -x['h_index'], x['institution']))[:10]

    # 按发文量排序
    top_publications = sorted(results,
                              key=lambda x: (-x['publications'], -x['total_citations'], x['institution']))[:10]

    # 按H指数排序
    top_hindex = sorted(results,
                        key=lambda x: (-x['h_index'], -x['total_citations'], x['institution']))[:10]

    return top_citations, top_publications, top_hindex


def print_top_list(data, title):
    """通用打印函数"""
    print(f"\n{'=' * 30} {title} {'=' * 30}")
    print("{:<60} {:<12} {:<15} {:<10}".format(
        "Institution", "Publications", "Total Citations", "H-index"))
    print("-" * 100)
    for item in data:
        print("{:<60} {:<12} {:<15} {:<10}".format(
            item['institution'],
            item['publications'],
            item['total_citations'],
            item['h_index']
        ))


def print_specific_columns(data, columns, title):
    """通用打印函数，指定显示的列"""
    column_titles = {
        'publications': ('Publications', 12),
        'total_citations': ('Total Citations', 15),
        'h_index': ('H-index', 10)
    }

    # 生成表头
    header = "{:<60}".format("Institution")
    for col in columns:
        title_part = column_titles[col][0]
        width = column_titles[col][1]
        header += " {:<{}}".format(title_part, width)

    print(f"\n{'=' * 30} {title} {'=' * 30}")
    print(header)
    print("-" * (60 + sum(
        [ct[1] + 1 for ct in column_titles.values() if ct[0] in [column_titles[c][0] for c in columns]])))

    # 打印数据行
    for item in data:
        line = "{:<60}".format(item['institution'])
        for col in columns:
            width = column_titles[col][1]
            line += " {:<{}}".format(item[col], width)
        print(line)


if __name__ == "__main__":
    all_results = analyze_c3_institutions("data/data.jsonl")
    top_citations, top_pubs, top_hindex = generate_top_lists(all_results)

    # 输出总被引排行榜
    print_specific_columns(top_citations,
                           ['total_citations'],
                           "Top 10 Institutions by Total Citations")

    # 输出发文量排行榜
    print_specific_columns(top_pubs,
                           ['publications'],
                           "Top 10 Institutions by Publications")

    # 输出H指数排行榜
    print_specific_columns(top_hindex,
                           ['h_index'],
                           "Top 10 Institutions by H-index")