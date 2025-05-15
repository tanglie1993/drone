import re


def parse_records(file_path):
    """解析WOS格式的文本文件，分割成独立记录"""
    records = []
    current_record = []
    in_record = False

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            stripped_line = line.strip()

            # 检测记录开始（PT字段）
            if re.match(r'^PT\s', stripped_line):
                if in_record:
                    records.append(current_record)
                current_record = [stripped_line]
                in_record = True
            # 检测记录结束（ER字段）
            elif in_record and stripped_line == 'ER':
                current_record.append(stripped_line)
                records.append(current_record)
                current_record = []
                in_record = False
            # 记录内容处理
            elif in_record:
                current_record.append(stripped_line)

    return records


def parse_record_fields(record_lines):
    """解析单条记录的字段内容（新增摘要和作者解析）"""
    data = {'TI': '', 'PY': 0, 'TC': 0, 'AB': '', 'AU': []}
    current_field = None

    for line in record_lines:
        # 检测字段标识（如TI/AB/AU等）
        if re.match(r'^[A-Z]{1,2}\d?\s', line[:3]):
            field_code = line[:2]
            content = line[3:].strip()
            current_field = field_code

            if field_code == 'AU':
                data['AU'].append(content)
            elif field_code in data:
                data[field_code] = content
        else:
            # 处理多行字段的延续内容
            stripped_line = line.strip()
            if current_field == 'AU' and data['AU']:
                data['AU'][-1] += ' ' + stripped_line
            elif current_field in data:
                data[current_field] += ' ' + stripped_line

    # 数据类型转换
    try:
        data['PY'] = int(data['PY']) if data['PY'] else 0
    except:
        data['PY'] = 0

    try:
        data['TC'] = int(data['TC']) if data['TC'] else 0
    except:
        data['TC'] = 0

    return {
        'title': data['TI'].strip(),
        'abstract': data['AB'].strip(),
        'authors': '; '.join(data['AU']),
        'year': data['PY'],
        'citations': data['TC']
    }


# 主程序
if __name__ == '__main__':
    # 读取文件并解析记录
    records = parse_records('data/data.txt')  # 替换为你的文件路径

    # 筛选并处理符合条件的记录
    high_cited = []
    for rec in records:
        parsed = parse_record_fields(rec)
        if parsed['year'] >= 2000 and parsed['citations'] > 0:
            high_cited.append((
                parsed['title'],
                parsed['abstract'],
                parsed['authors'],
                parsed['citations']
            ))

    # 按被引次数降序排序
    high_cited_sorted = sorted(high_cited, key=lambda x: (-x[3], x[0]))[:20]

    # 打印结果（新增摘要和作者输出）
    print("高频被引文章（2000年及以后）：")
    for idx, (title, abstract, authors, cites) in enumerate(high_cited_sorted, 1):
        print(f"{idx}. 标题：{title}")
        # print(f"   摘要：{abstract}")
        # print(f"   作者：{authors}")
        print(f"   被引次数：{cites}\n")