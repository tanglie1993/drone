from collections import defaultdict

# 读取文件
with open('data/data.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 初始化统计变量
journal_count = defaultdict(int)  # 期刊发文数量
journal_citations = defaultdict(int)  # 期刊总被引次数
current_journal = None  # 当前文献的期刊名称
current_citations = 0  # 当前文献的被引次数

for line in lines:
    # 提取期刊名称
    if line.startswith('SO'):
        current_journal = line.strip().split('SO ')[-1].strip()
    # 提取被引次数
    elif line.startswith('TC'):
        current_citations = int(line.strip().split()[-1])
        # 更新期刊统计
        if current_journal:
            journal_count[current_journal] += 1
            journal_citations[current_journal] += current_citations

# 计算各期刊的平均被引次数
journal_avg_citations = {
    journal: journal_citations[journal] / journal_count[journal]
    for journal in journal_count
}

# 按发文数量排序
sorted_journals_by_count = sorted(journal_count.items(), key=lambda x: x[1], reverse=True)
# 按平均被引次数排序
sorted_journals_by_avg_citations = sorted(journal_avg_citations.items(), key=lambda x: x[1], reverse=True)

# 输出高频期刊（按发文数量）
print("高频期刊统计（按发文数量）：")
for journal, count in sorted_journals_by_count[:20]:  # 输出前20个
    print(f"{journal}: 发文数量 {count} 次，平均被引次数 {journal_avg_citations[journal]:.2f} 次")

# 输出高频期刊（按平均被引次数）
print("\n高频期刊统计（按平均被引次数）：")
for journal, avg_citations in sorted_journals_by_avg_citations[:20]:  # 输出前20个
    print(f"{journal}: 平均被引次数 {avg_citations:.2f} 次，发文数量 {journal_count[journal]} 次")