import json
import re
from chardet import detect


def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read(10000)  # 读取前10000字节用于检测编码
    return detect(rawdata)['encoding']


def convert_wos_to_jsonl(input_file, output_file):
    # 自动检测文件编码
    encoding = detect_encoding(input_file)
    print(f"检测到文件编码: {encoding}")

    # 字段处理配置
    target_fields = {'TI', 'AB', 'DE'}  # 需要保留的字段
    field_pattern = re.compile(r'^([A-Z][A-Z0-9])[ \t]')  # 字段匹配正则

    with open(input_file, 'r', encoding=encoding, errors='replace') as infile, \
            open(output_file, 'w', encoding='utf-8') as outfile:

        current_record = {}  # 当前处理中的记录
        current_field = None  # 当前处理的字段
        current_content = []  # 当前字段内容缓存

        def finalize_field():
            """完成当前字段的收集"""
            nonlocal current_field, current_content
            if current_field in target_fields and current_content:
                # 合并多行内容并去除多余空格
                current_record[current_field] = ' '.join(current_content).strip()
            current_field = None
            current_content = []

        def finalize_record():
            """完成并写入当前记录"""
            nonlocal current_record
            finalize_field()  # 确保最后一个字段被处理
            if current_record:
                json_line = json.dumps(current_record, ensure_ascii=False)
                outfile.write(json_line + '\n')
                current_record.clear()

        for line in infile:
            # 匹配字段开头（两个字符：字母+字母/数字）
            if match := field_pattern.match(line):
                field = match.group(1)
                content = line[2:].lstrip()  # 去除字段标记和空格

                # 处理特殊字段
                if field == 'PT':  # 新记录开始
                    finalize_record()  # 完成前一个记录
                    current_record = {'PT': content.strip()}
                    continue
                elif field == 'ER':  # 记录结束
                    finalize_record()
                    continue

                # 处理目标字段
                if field in target_fields:
                    finalize_field()  # 完成前一个字段
                    current_field = field
                    current_content.append(content.strip())
                else:
                    finalize_field()  # 非目标字段直接跳过
            else:
                # 处理多行内容（仅限目标字段）
                if current_field in target_fields:
                    current_content.append(line.strip())

        # 处理文件末尾可能未完成的记录
        finalize_record()


# 使用示例
try:
    convert_wos_to_jsonl('data/expanded_full_data_output.jsonl', 'data/filtered.jsonl')
    print("转换成功完成！")
except Exception as e:
    print(f"处理过程中出现错误: {str(e)}")