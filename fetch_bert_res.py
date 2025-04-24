import requests
import json
import re
from tqdm import tqdm

API_URL = 'http://quickstart-deploy-20250411-5ixi.1682401066495619.cn-shanghai.pai-eas.aliyuncs.com/'
API_TOKEN = 'MTM0NDBlNmUzYjZlOGQ0ZjdhNDRjOGY1NTcyMzA2MTVmODYzYjdmNQ=='
HEADERS = {"Authorization": API_TOKEN}
MAX_TOKENS = 200  # 最大token限制


def truncate_text(text, max_tokens):
    """裁剪文本到指定token数量（基于空格分词）"""
    tokens = text.split()
    if len(tokens) <= max_tokens:
        return text
    return ' '.join(tokens[:max_tokens])


def build_api_payload(ti, ab, de):
    """构建API请求负载，确保不超过token限制"""
    # 计算各部分最大允许长度（保留标题完整性）
    max_ti = min(len(ti.split()), 100)  # 标题最多100个token
    max_ab = MAX_TOKENS - max_ti - 20  # 预留20个token给连接词

    truncated_ti = truncate_text(ti, max_ti)
    truncated_ab = truncate_text(ab, max_ab)

    return {
        "data": [f"Title: {truncated_ti} Abstract: {truncated_ab}"]
    }


def process_jsonl(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, \
            open(output_file, 'w', encoding='utf-8') as outfile:

        for line in tqdm(infile, desc='Processing'):
            try:
                data = json.loads(line.strip())
                ti = data.get('TI', '')
                ab = data.get('AB', '')
                de = data.get('DE', '')

                # 构建裁剪后的请求体
                payload = build_api_payload(ti, ab, de)

                # 调试输出（可选）
                total_tokens = len(payload["data"][0].split())
                print(f"Sent tokens: {total_tokens}")  # 验证token数量

                # 调用API
                response = requests.post(
                    url=API_URL,
                    headers=HEADERS,
                    json=payload,
                    timeout=30
                )

                # 处理响应
                result = {
                    "original_data": {
                        "TI": ti,
                        "AB": ab,
                        "DE": de
                    },
                    "truncated_input": payload["data"][0],
                    "status": "success" if response.status_code == 200 else "failed",
                    "response": response.json() if response.status_code == 200 else {
                        "status_code": response.status_code,
                        "text": response.text
                    }
                }

                outfile.write(json.dumps(result, ensure_ascii=False) + '\n')

            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)} | 行内容: {line[:50]}...")
            except Exception as e:
                print(f"处理异常: {str(e)}")
                outfile.write(json.dumps({
                    "error": str(e),
                    "original_line": line.strip()[:200] + "..." if len(line) > 200 else line.strip()
                }) + '\n')


if __name__ == "__main__":
    input_file = 'data/expanded_full_data_output.jsonl'
    output_file = 'data/truncated_classified_results.jsonl'

    print("开始处理分类任务（带裁剪功能）...")
    process_jsonl(input_file, output_file)
    print(f"\n处理完成！裁剪后的结果已保存到 {output_file}")