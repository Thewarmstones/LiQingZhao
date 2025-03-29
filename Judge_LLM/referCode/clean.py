import os,json
import re

pattern = r"split_byword_text\\(.*?)\.txt"


input_folder = './output'

output_path = './cleaned_data/word_gen_data.json'
error_path = './cleaned_data/error.json'
stastic_path = './cleaned_data/stastic.json'

cleaned_data = []
error_files = []

cnt1 = cnt2 = cnt3 = cnt4 = cnt5 = 0

for file in os.listdir(input_folder):
    if file.endswith('.txt') or file.startswith('error'):
        continue
    with open(os.path.join(input_folder, file), 'r',encoding='utf-8') as f:
        data = json.load(f)
    # print(file)
    match = re.search(pattern, data['ref_path'])
    if match:
        word = match.group(1)
    gen_content = []
    
    instruction,output,content = "","",""
    cnt = len(error_files)
    for line in data['gen_content'].split("\n"):
        line = line.strip()
        if line == "":
            continue
        if ' ' in line:
            line = line.replace(' ','')
        if '-' in line:
            line = line.replace('-','')

        if line.startswith("用户"):
            if line.startswith("用户："):
                instruction = line.replace("用户：","")
            elif line.startswith("用户:"):
                instruction = line.replace("用户:","")
            else:
                error_files.append(file)
                break
        elif line.startswith("上下文"):
            if line.startswith("上下文："):
                content = line.replace("上下文：","")
            elif line.startswith("上下文:"):
                content = line.replace("上下文:","")
            else:
                error_files.append(file)
                break
            if instruction == "" or content == "":
                error_files.append(file)
                break
        elif line.startswith("李清照"):
            if line.startswith("李清照："):
                output = line.replace("李清照：","")
            elif line.startswith("李清照:"):
                output = line.replace("李清照:","")
            else:
                error_files.append(file)
                break
            if instruction == "" or content == "" or output == "":
                error_files.append(file)
                break
            gen_content.append(
                {
                    "instruction": instruction,
                    "content": content,
                    "output": output
                }
            )
            cnt3 += len(instruction)
            cnt4 += len(content)
            cnt5 += len(output)
            instruction,output,content = "","",""

    if cnt == len(error_files):
        cnt1 += 1
        cnt2 += len(gen_content)
        cleaned_data.append({
            "ref_path": data['ref_path'],
            "ref_content": data['ref_content'],
            "word": word,
            "gen_content": gen_content,
        })

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
with open(error_path, 'w', encoding='utf-8') as f:
    json.dump(error_files, f, ensure_ascii=False, indent=4)
with open(stastic_path, 'w', encoding='utf-8') as f:
    json.dump({
        "total_token": cnt1,
        "total_gen_dia": cnt2,
        "total_instruction": cnt3,
        'average_instruction': cnt3/cnt2,
        "total_content": cnt4,
        'average_content': cnt4/cnt2,
        "total_output": cnt5,
        'average_output': cnt5/cnt2,
    }, f, ensure_ascii=False, indent=4)