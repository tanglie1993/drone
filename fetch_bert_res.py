import requests
import json
from tqdm import tqdm  # 用于显示进度条

API_URL = 'http://quickstart-deploy-20250407-w1o1.1682401066495619.cn-shanghai.pai-eas.aliyuncs.com/'
API_TOKEN = 'YzFkM2E5NmUxMjFhYTcxOTc1MWYyOGMzZTExMzk5MDAwYmM2NzMxMQ=='
HEADERS = {"Authorization": API_TOKEN}


def process_jsonl(input_file, output_file):
	"""处理JSONL文件并提交API分类"""
	with open(input_file, 'r', encoding='utf-8') as infile, \
			open(output_file, 'w', encoding='utf-8') as outfile:

		linecount = 0
		cutoff = 1936

		for line in tqdm(infile, desc='Processing'):
			linecount = linecount + 1
			if linecount <= cutoff:
				continue
			try:
				# 解析JSON行
				data = json.loads(line.strip())
				ti = data.get('TI', '')
				ab = data.get('AB', '')
				de = data.get('DE', '')

				# 构建API请求体
				request_body = {
					"data": [f"Title: {ti} Abstract: {ab}"]
				}

				# 调用API
				response = requests.post(
					url=API_URL,
					headers=HEADERS,
					json=request_body,
					timeout=30  # 设置超时时间
				)

				# 处理响应
				if response.status_code == 200:
					result = {
						"original_data": data,
						"classification": response.json(),
						"status": "success"
					}
					print(result)
				else:
					result = {
						"original_data": data,
						"error": f"API error: {response.status_code}",
						"response": response.text,
						"status": "failed"
					}

				# 写入结果
				outfile.write(json.dumps(result, ensure_ascii=False) + '\n')

			except json.JSONDecodeError as e:
				print(f"JSON解析错误: {str(e)} | 行内容: {line}")
			except requests.exceptions.RequestException as e:
				print(f"API请求异常: {str(e)}")
				# 记录失败信息
				result = {
					"original_data": line.strip(),
					"error": str(e),
					"status": "failed"
				}
				outfile.write(json.dumps(result) + '\n')


# 使用示例
input_file = 'data/expanded_full_data_output.jsonl'  # 输入的JSONL文件路径
output_file = 'classified_results1.jsonl'  # 输出结果文件路径

print("开始处理分类任务...")
process_jsonl(input_file, output_file)
print(f"\n处理完成！结果已保存到 {output_file}")