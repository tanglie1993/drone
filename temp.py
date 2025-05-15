import json
import re
from collections import defaultdict


def wos_to_jsonl(input_path, output_path):
    """流式处理WOS文件，直接生成JSONL"""
    field_start = re.compile(r'^([A-Z]{2}|[A-Z]\d)\s(.*)')
    current_record = defaultdict(list)
    current_field = None

    with open(input_path, 'r', encoding='utf-8-sig') as fin, \
            open(output_path, 'w', encoding='utf-8') as fout:

        for line in fin:
            line = line.rstrip('\n').lstrip('\ufeff').rstrip('\r')

            # 处理记录结束
            if line == 'ER':
                if current_record:
                    # 转换值为字符串或列表
                    record = {
                        k: v[0] if len(v) == 1 else v
                        for k, v in current_record.items()
                    }
                    fout.write(json.dumps(record, ensure_ascii=False) + '\n')
                    current_record = defaultdict(list)
                current_field = None
                continue

            # 字段开始检测
            if match := field_start.match(line):
                current_field = match.group(1)
                value_part = match.group(2).strip()
                if value_part:
                    current_record[current_field].append(value_part)
                continue

            # 延续行处理
            if current_field and (line.startswith('   ') or not field_start.match(line)):
                if current_record[current_field]:
                    # 保留原始换行符号
                    current_record[current_field][-1] += '\n' + line.strip()
                else:
                    current_record[current_field].append(line.strip())


if __name__ == "__main__":
    wos_to_jsonl("data/data.txt", "data.jsonl")