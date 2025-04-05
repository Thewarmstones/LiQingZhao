import os
input_path = "all_table/location_work.txt"

output_folder = './new/location_work'  # 输出评测文件夹路径
os.makedirs(output_folder, exist_ok=True)

with open(input_path, 'r', encoding='utf-8') as f:
    data = [line.strip() for line in f.readlines() if line.strip() and not line.endswith('岁。\n')]

i = 0
for index in range(0,len(data),10):
    ele = '\n'.join(data[index:index+10])
    with open(os.path.join(output_folder, f'location_work_{i}.txt'), 'w', encoding='utf-8') as f:
        f.write(ele)
    i += 1