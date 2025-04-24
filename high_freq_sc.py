from collections import defaultdict, Counter
import re


def process_file(filename):
    # 初始化变量
    wc_before_2021 = []
    wc_after_2020 = []
    current_year = None
    current_wc = []
    is_wc = False

    # 正则匹配字段开头
    field_pattern = re.compile(r'^[A-Z]{2}[ \t]')

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            # 提取年份
            if line.startswith('PY'):
                current_year = int(line.strip().split()[-1])

            # 检测是否为新字段（非WC字段）
            if field_pattern.match(line) and not line.startswith('WC'):
                if is_wc:
                    # 结束当前WC字段的读取
                    wc_content = ' '.join(current_wc)
                    # 按时间段分类
                    if current_year:
                        if current_year < 2021:
                            wc_before_2021.append(wc_content)
                        else:
                            wc_after_2020.append(wc_content)
                    current_wc = []
                    is_wc = False
                continue

            # 处理WC字段
            if line.startswith('WC'):
                is_wc = True
                current_wc.append(line[2:].strip())  # 去掉"WC"前缀
            elif is_wc:
                current_wc.append(line.strip())

    # 处理最后一个WC字段（如果存在）
    if is_wc and current_wc:
        wc_content = ' '.join(current_wc)
        if current_year:
            if current_year < 2021:
                wc_before_2021.append(wc_content)
            else:
                wc_after_2020.append(wc_content)

    return wc_before_2021, wc_after_2020


def parse_categories(wc_list):
    """解析WC字段内容（分号分割学科）"""
    categories = []
    for entry in wc_list:
        # 按分号分割，并去除空白字符
        for category in entry.split(';'):
            category = category.strip()
            if category:
                categories.append(category)
    return categories


# 主程序
filename = 'data/data.txt'
wc_before, wc_after = process_file(filename)

# 解析学科分类
categories_before = parse_categories(wc_before)
categories_after = parse_categories(wc_after)

# 统计学科频率
counter_before = Counter(categories_before)
counter_after = Counter(categories_after)

# 输出结果
print("2020年及之前最高频学科：")
if counter_before:
    for i in range(0, 10):
        most_common_before = counter_before.most_common(10)[i]
        print(f"{most_common_before[0]}: {most_common_before[1]}次")
else:
    print("无数据")

print("\n2021年及之后最高频学科：")
if counter_after:
    for i in range(0, 10):
        most_common_after = counter_after.most_common(10)[i]
        print(f"{most_common_after[0]}: {most_common_after[1]}次")
else:
    print("无数据")