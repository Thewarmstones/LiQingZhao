from openai import OpenAI
from collections import defaultdict
import json

promptQuery = \
"""
请扮演指定角色和我进行交流对话:
-- 角色 --
李清照
-- 语言风格 --
使用白话风格进行交流，不要文邹邹的
-- 输入 --
{query}
-- 输出 --"""


# 配置 OpenAI 客户端，指向本地 Ollama 服务
client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama 的 OpenAI 兼容接口地址
    api_key="ollama",                     # Ollama 不需要真实的 API Key，但需要提供一个占位值
)

model_list = ["qwen2.5:7b","gemma3:12b","llama3.1:8b"]
mapping = {
    "qwen2.5:7b":"Qwen2.5-7B",
    "gemma3:12b":"Gemma3-12B",
    "llama3.1:8b":"Llama3.1-8B"
}


# 读取问题数据
# with open('****', 'r', encoding='utf-8') as f:
#     data = f.read()

# 测试问题
questions = ["你是博家之祖吗","你平时有什么爱好","你如何看待夫妻间的学术交流"]


model_QA = defaultdict(list)

for modelName in model_list:
    for question in questions:
        response = client.chat.completions.create(
            model=modelName,
            messages=[
                {"role": "system", "content": "你是李清照，号易安居士。早年生活优渥，家学深厚，婚后与丈夫赵明诚共同致力于书画金石的搜集整理。后因金兵南侵，流落南方，历经国破家亡，晚景孤苦，情感转为凄怆沉郁。"},
                {"role": "user", "content": promptQuery.replace("{query}",question)}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        # 模型的回复
        ai_response = response.choices[0].message.content
        # print(ai_response)
        model_QA[mapping[modelName]].append(
                {
                    'query':question,
                    'response':ai_response,
                    'annotation':""
                }
            )

# 打印各个模型的回复
for model_info in model_QA:
    for qa in model_QA[model_info]:
        print(qa['query'])
        print(qa['response'])
        print(qa['annotation'])
        print("*"*50)

exit()
with open("model_QA.json","w",encoding="utf-8") as f:
    json.dump(model_QA,f,ensure_ascii=False,indent=4)


