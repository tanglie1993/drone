import matplotlib.pyplot as plt
from collections import defaultdict

# 读取文件
with open('data/data.txt', 'r', encoding='utf-8') as file:
    lines = file.readlines()

# 统计年份
year_count = defaultdict(int)

for line in lines:
    if line.startswith('PY'):
        year = line.split()[-1]  # 提取年份
        year_count[year] += 1

# 排序年份
sorted_years = sorted(year_count.keys())
counts = [year_count[year] for year in sorted_years]

# 打印年份及对应数量（新增部分）
print("Year : Publications")
for year, count in zip(sorted_years, counts):
    print(f"{year} : {count}")

# 绘制柱状图
plt.figure(figsize=(10, 6))
plt.bar(sorted_years, counts, color='skyblue')
plt.xlabel('Year')
plt.ylabel('Number of Publications')
plt.title('Number of Publications per Year')
plt.xticks(rotation=45)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# 显示图表
plt.tight_layout()
plt.show()