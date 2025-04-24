import json

def extract_true_tis(jsonl_file):
    true_tis = set()
    with open(jsonl_file, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            if data['status'] == 'success':
                for response in data['response']:
                    if response['label'] == 'true':
                        true_tis.add(data['original_data']['TI'].strip())
    return true_tis

def filter_and_write_records(data_file, output_file, true_tis):
    with open(data_file, 'r', encoding='utf-8') as f_in, \
         open(output_file, 'w', encoding='utf-8') as f_out:
        current_record = []
        current_ti = None
        in_ti = False
        for line in f_in:
            if line.startswith('ER'):
                # 检查当前记录的TI是否匹配
                if current_ti and current_ti in true_tis:
                    f_out.write(''.join(current_record))
                    f_out.write(line)
                current_record = []
                current_ti = None
                in_ti = False
            else:
                current_record.append(line)
                # 处理TI字段
                if line.startswith('TI '):
                    current_ti = line[3:].strip()
                    in_ti = True
                elif in_ti and line.startswith('   '):  # 多行TI的缩进部分
                    current_ti += ' ' + line.strip()
                else:
                    in_ti = False

# 主流程
jsonl_file = 'data/truncated_classified_results.jsonl'  # 替换为你的JSONL文件路径
data_file = 'data/expanded_full_data.txt'      # 替换为你的data.txt路径
output_file = 'data.txt'  # 输出文件路径

true_tis = extract_true_tis(jsonl_file)
filter_and_write_records(data_file, output_file, true_tis)

print(f"筛选完成，结果已写入 {output_file}")