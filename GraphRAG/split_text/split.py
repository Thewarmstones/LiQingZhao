import os
input_path = ""

output_folder = './peom'  # 输出评测文件夹路径
os.makedirs(output_folder, exist_ok=True)

with open(input_path, 'r', encoding='utf-8') as f:
    data = f.read()

newdata = data.split('\n\n')

for index in range(len(newdata)):
    ele = newdata[index].strip()
    if not ele:
        continue
    with open(os.path.join(output_folder, f'poem_{index}'), 'w', encoding='utf-8') as f:
        f.write(ele)
