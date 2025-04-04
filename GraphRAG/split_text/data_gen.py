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
input_folder = './poem'  # 输入模型回复文件夹路径
output_folder = './poem_explain'  # 输出评测文件夹路径
error_folder = './error' # 错误文件路径
os.makedirs(output_folder, exist_ok=True)
os.makedirs(error_folder, exist_ok=True)


error_f = open(os.path.join(error_folder,'judge_wrong.txt'), 'a', encoding='utf-8')

for sub_folder in os.listdir(input_folder):
    if sub_folder.endswith('.txt'):
        continue
    sub_input_folder = os.path.join(input_folder,sub_folder)
    sub_output_folder = os.path.join(output_folder,sub_folder)
    os.makedirs(sub_output_folder, exist_ok=True)
    # 遍历子文件夹中的所有 .txt 文件
    for file_name in os.listdir(sub_input_folder):
        # if not file_name.endswith('.txt'):
        #     continue
        input_path = os.path.join(sub_input_folder, file_name)
        outpath = os.path.join(sub_output_folder,file_name+'.txt')
        if file_name+'.txt' in os.listdir(sub_output_folder):
            print(file_name+"已存在")
            continue
        # 写入文件名，后续记录该文件中出现的错误
        error_f.write('*' * 50 +'\n' + file_name + ':\n')

        with open(input_path, 'r', encoding='utf-8') as f:
            data = f.read()

        new_prompt = prompt_info.replace('{text_content}', data)
        try:
            completion = client.chat.completions.create(
                model="gpt-4-turbo-2024-04-09",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": new_prompt}
                ]
            )
            ai_response = completion.choices[0].message.content
            print(ai_response)
        except Exception:
            ## 重写
            error_f.write(input_path + '\n')
            continue

        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(ai_response)

