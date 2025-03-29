# 目标:清理ai的原始评分数据，抽取评分、评价内容，标记 并保存
# 拓展:后续会根据各维度指标的评分可视化，评价内容或许可以用jieba分词抽取共性评价？待定
import os
import re
import json

# 定义输入和输出文件夹路径
input_folder = './ai_output'  # 输入文件夹路径
output_folder = './clean_data'  # 输出文件夹路径
error_folder = './error' # 错误文件路径
os.makedirs(output_folder, exist_ok=True)
os.makedirs(error_folder, exist_ok=True)

class NegativeAgeError(Exception):
    def __init__(self, message="出现数据错误"):
        self.message = message
        super().__init__(self.message)


# 设计正则匹配模式
pattern = r"aaa(.*?)bbb"
# 注意错误抛出
# matches = re.findall(pattern, "aaa算法i分红哎bbb asdoihdaaabbbbbbaaadbbb")
# if len(matches) > 1 or len(matches) == 0:
#     raise NegativeAgeError("错误") # 这里自定义了一个异常类
# exit()



file_list = os.listdir(input_folder)


for file in file_list:
    if file.endswith('.json'):
        continue
    new_data = []
    with open(os.path.join(input_folder, file), 'r', encoding='utf-8') as f:
        judge_data = json.load(f)
    # 根据文本内容进行处理
    # 首先是split by换行符，然后正则匹配进行处理
    # 匹配失败的数据存储在error_folder文件夹下
    pass
    with open(os.path.join(output_folder, file), 'w', encoding='utf-8') as f:
        json.dump(judge_data, f, ensure_ascii=False, indent=4)