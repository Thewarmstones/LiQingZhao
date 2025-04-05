import os
input_path = "./ori_text/graphdata.txt"

# output_folder = './poem'  # 输出评测文件夹路径
# os.makedirs(output_folder, exist_ok=True)

with open(input_path, 'r', encoding='utf-8') as f:
    data = f.read()

with open('all_table/works.txt', 'r', encoding='utf-8') as f:
    data2 = f.readlines()
# print(data2)

for i in range(len(data2)):
    ele = data2[i]
    if ele=='\n':
        continue
    print(ele)
    if ele in data:
        print(ele)
        data = data.replace(ele, '')
data = [line.strip() for line in data.split('\n') if line.strip() ]
with open('all_table/envent2.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(data))
