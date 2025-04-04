# 对于模型生成的回复进行评估
# 利用GPT自动评估
# 整理好标注和原始文本


import os
import json
from tqdm import tqdm
from openai import OpenAI

## 导入提示词
from prompt import prompt_info


# 初始化 OpenAI 客户端
client = OpenAI(
    base_url='https://www.apigptopen.xyz/v1',
    api_key='sk-YB18uqLFQ64gVvjpUnwzzi9jxH7o3w36sXRmCtaZUmKb04uk'
)

# 定义输入和输出文件夹路径
input_folder = './ai_output'  # 输入模型回复文件夹路径
output_folder = './judge_output'  # 输出评测文件夹路径
error_folder = './error' # 错误文件路径
os.makedirs(output_folder, exist_ok=True)
os.makedirs(error_folder, exist_ok=True)


error_f = open(os.path.join(error_folder,'judge_wrong.txt'), 'a', encoding='utf-8')

# 遍历子文件夹中的所有 .txt 文件
for filelist_name in os.listdir(input_folder):
    if not filelist_name.endswith('.json'):
        continue
    input_path = os.path.join(input_folder, filelist_name)
    output_path = os.path.join(input_folder, 'judge_' + filelist_name)

    # 写入文件名，后续记录该文件中出现的错误
    error_f.write('*'*50+'\n'+filelist_name+':\n')

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ## 重写
    for i in tqdm(range(len(data))):
        ele = data[i]
        new_prompt = promptJudge.replace('{{title}}', ele['title']).replace('{{content}}', ele['content']).replace('{{comment}}', ele['comment']).replace('{{anno}}', ele['anno']).replace('{{conversations}}',str(ele['conversations']))
        data[i]['judge'] = "###WRONG###"
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
            ## 重写
            error_f.write(ele['idx'] + '\n')
            continue

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

