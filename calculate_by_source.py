from collections import defaultdict




def analyze_journals(file_path):
    """执行期刊分析"""
    journal_data = defaultdict(lambda: {
        'count': 0,
        'total_citations': 0,
        'articles': []
    })

    # 处理每条文献记录
    for record in parse_wos_records(file_path):
        journal = record['journal']
        journal_data[journal]['count'] += 1
        journal_data[journal]['total_citations'] += record['citations']

        # 存储文章详细信息（限制存储字段）
        journal_data[journal]['articles'].append({
            'citations': record['citations'],
            'title': record['title'],
            'authors': record['authors'][:3] + ['...'] if len(record['authors']) > 3 else record['authors'],
            'abstract': record['abstract'][:200] + '...' if len(record['abstract']) > 200 else record['abstract']
        })

    # 计算附加指标
    for journal in journal_data:
        data = journal_data[journal]
        data['avg_citations'] = data['total_citations'] / data['count'] if data['count'] else 0

        # 按被引排序文章
        data['top_articles'] = sorted(data['articles'],
                                      key=lambda x: (-x['citations'], x['title']))[:5]

    return journal_data


def generate_report(journal_data, top_n=20):
    """生成分析报告"""
    # 按发文量排序
    sorted_by_count = sorted(journal_data.items(),
                             key=lambda x: -x[1]['count'])[:top_n]

    # 按均被引排序
    sorted_by_avg = sorted(journal_data.items(),
                           key=lambda x: -x[1]['avg_citations'])[:top_n]

    # 输出结果
    print("=== 高频期刊统计（按发文量） ===")
    for journal, data in sorted_by_count:
        print(f"\n▨ 期刊: {journal}")
        print(f"  发文量: {data['count']} 篇")
        print(f"  总被引: {data['total_citations']} 次")
        print(f"  篇均被引: {data['avg_citations']:.2f} 次")

        # print("\n  高被引论文TOP5:")
        # for idx, art in enumerate(data['top_articles'], 1):
        #     print(f"  {idx}. [{art['citations']}次] {art['title']}")
        #     print(f"     作者: {', '.join(art['authors'])}")
        #     if art['abstract']:
        #         print(f"     摘要: {art['abstract']}")

    print("\n\n=== 高频期刊统计（按篇均被引） ===")
    for journal, data in sorted_by_avg:
        print(f"\n▨ 期刊: {journal}")
        print(f"  篇均被引: {data['avg_citations']:.2f} 次")
        print(f"  发文量: {data['count']} 篇")
        print(f"  总被引: {data['total_citations']} 次")


from collections import defaultdict
import re


def clean_line_start(line):
    """去除行首的特殊不可见字符"""
    # 移除BOM标记和零宽空格
    return line.lstrip('\ufeff').lstrip('\u200b').lstrip()


def parse_wos_records(file_path):
    """解析WOS格式文件，生成文献记录生成器"""
    current_record = {}
    in_record = False

    with open(file_path, 'r', encoding='utf-8-sig') as file:  # 使用utf-8-sig处理BOM
        for raw_line in file:
            # 处理行首特殊字符
            line = clean_line_start(raw_line).rstrip('\n')

            # 检测记录开始
            if re.match(r'^PT[ \t]', line):
                in_record = True
                current_record = {
                    'journal': None,
                    'citations': 0,
                    'title': '',
                    'authors': [],
                    'abstract': ''
                }
                continue

            # 检测记录结束
            if line == 'ER':
                in_record = False
                if current_record.get('journal'):
                    yield current_record
                continue

            if in_record:
                # 解析期刊名称（处理可能存在的冒号）
                if re.match(r'^SO[ \t:]', line):
                    current_record['journal'] = line.split(maxsplit=1)[-1].strip(' :')

                # 解析被引次数（兼容不同分隔符）
                elif re.match(r'^TC[ \t:]', line):
                    parts = re.split(r'[ \t:]+', line, maxsplit=1)
                    if len(parts) > 1:
                        current_record['citations'] = int(parts[1].strip().split()[0])

                # 解析标题（处理多行情况）
                elif re.match(r'^TI[ \t:]', line):
                    current_record['title'] = re.sub(r'^TI[ \t:]*', '', line)
                elif re.match(r'^[ \t]', line) and current_record['title'] is not None:
                    current_record['title'] += ' ' + line.strip()

                # 解析作者（处理多行及分隔符）
                elif re.match(r'^AU[ \t:]', line):
                    authors = re.split(r';|,', re.sub(r'^AU[ \t:]*', '', line))
                    current_record['authors'].extend([a.strip() for a in authors if a.strip()])
                elif re.match(r'^[ \t]', line) and current_record['authors']:
                    line_authors = re.split(r';|,', line.strip())
                    current_record['authors'].extend([a.strip() for a in line_authors if a.strip()])

                # 解析摘要（处理多行）
                elif re.match(r'^AB[ \t:]', line):
                    current_record['abstract'] = re.sub(r'^AB[ \t:]*', '', line)
                elif re.match(r'^[ \t]', line) and current_record['abstract'] is not None:
                    current_record['abstract'] += ' ' + line.strip()


# ...（保持analyze_journals和generate_report函数不变）...

if __name__ == "__main__":
    journal_stats = analyze_journals('data/data.txt')
    generate_report(journal_stats)