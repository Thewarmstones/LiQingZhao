# 对于模型生成的回复进行评估
# 利用GPT自动评估
# 整理好标注和原始文本


import os
import json
from tqdm import tqdm
from openai import OpenAI

## 导入提示词
from Prompt import promptJudge


# 初始化 OpenAI 客户端
client = OpenAI(
    base_url='https://www.apigptopen.xyz/v1',
    api_key='sk-YB18uqLFQ64gVvjpUnwzzi9jxH7o3w36sXRmCtaZUmKb04uk'
)

# 定义输入和输出文件夹路径
input_folder = './query_input'  # 输入文件夹路径
output_folder = './ai_output'  # 输出文件夹路径

os.makedirs(output_folder, exist_ok=True)




processed_files = set()

# 遍历子文件夹中的所有 .txt 文件
for filelist_name in os.listdir(input_folder):
    if filelist_name.startswith('judge'):
        continue
    input_path = os.path.join(input_folder, filelist_name)
    output_path = os.path.join(input_folder, 'judge_' + filelist_name)
    with open('poem/finnal_output/judge_wrong', 'a', encoding='utf-8') as f:
        f.write(input_path + '\n')
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    for i in tqdm(range(len(data))):
        ele = data[i]
        new_prompt = promptJudge.replace('{{title}}', ele['title']).replace('{{content}}', ele['content']).replace(
            '{{comment}}', ele['comment']).replace('{{anno}}', ele['anno']).replace('{{conversations}}',
                                                                                    str(ele['conversations']))
        try:
            completion = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": new_prompt}
                ]
            )
            ai_response = completion.choices[0].message.content
            data[i]['judge'] = ai_response
        except Exception:
            with open('poem/finnal_output/judge_wrong', 'a', encoding='utf-8') as f:
                f.write(ele['idx'] + '\n')
            continue
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

