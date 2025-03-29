import os,json
import re

pattern = r"split_byword_text\\(.*?)\.txt"


input_path = './evaluate/evaluate.json'

output_path = './cleaned_data/word_gen_data_evaluate.json'
error_path = './cleaned_data/error_evaluate.json'
stastic_path = './cleaned_data/stastic_evaluate.json'

cleaned_data = []
error_files = []

cnt1 = cnt2 = cnt3 = cnt4 = cnt5 = 0

with open(input_path, 'r',encoding='utf-8') as f:
    Data = json.load(f)
# print(file)




for data in Data:
    cnt = len(error_files)
    match = re.search(pattern, data['ref_path'])
    if match:
        word = match.group(1)
    gen_content = []
    instruction,output,content = "","",""
    
    evaluate_lines = data['evaluate'].split("\n")
    
    eval1,eval2,eval3 = "", "", ""
    for start,line in enumerate(evaluate_lines):
        if '内容准确性' in line:
            if len(line)<12:
                error_files.append(data)
                break
            eval1 = line
        elif '内容覆盖度' in line:
            if len(line)<12 or eval1=="":
                error_files.append(data)
                break
            eval2 = line
        elif '表达流畅度' in line:
            if len(line)<12 or eval1=="" or eval2=="":
                error_files.append(data)
                break
            eval3 = line
            break
    if eval1 == "" or eval2 == "" or eval3 == "":
        continue
    start += 1
    evaluate = [eval1,eval2,eval3]

    # for line in evaluate_lines[start:]:
    #     line = line.strip()
    #     if line == "":
    #         continue


    #     if line.startswith("用户"):
    #         if line.startswith("用户："):
    #             instruction = line.replace("用户：","")
    #         elif line.startswith("用户:"):
    #             instruction = line.replace("用户:","")
    #         else:
    #             error_files.append(data)
    #             break
    #     elif line.startswith("上下文"):
    #         if line.startswith("上下文："):
    #             content = line.replace("上下文：","")
    #         elif line.startswith("上下文:"):
    #             content = line.replace("上下文:","")
    #         else:
    #             error_files.append(data)
    #             break
    #         if instruction == "" or content == "":
    #             error_files.append(data)
    #             break
    #     elif line.startswith("李清照"):
    #         if line.startswith("李清照："):
    #             output = line.replace("李清照：","")
    #         elif line.startswith("李清照:"):
    #             output = line.replace("李清照:","")
    #         else:
    #             error_files.append(data)
    #             break
    #         if instruction == "" or content == "" or output == "":
    #             error_files.append(data)
    #             break
    #         gen_content.append(
    #             {
    #                 "instruction": instruction,
    #                 "content": content,
    #                 "output": output
    #             }
    #         )
    #         cnt3 += len(instruction)
    #         cnt4 += len(content)
    #         cnt5 += len(output)
    #         instruction,output,content = "","",""

    if cnt == len(error_files):
        # if len(gen_content) == 0:
        #     error_files.append(data)
        # else:
            # cnt1 += 1
            # cnt2 += len(gen_content)
        cleaned_data.append({
            "ref_path": data['ref_path'],
            "ref_content": data['ref_content'],
            "word": word,
            "gen_content": data['gen_content'],
            "evaluate": evaluate,
            
        })


with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
with open(error_path, 'w', encoding='utf-8') as f:
    json.dump(error_files, f, ensure_ascii=False, indent=4)
# with open(stastic_path, 'w', encoding='utf-8') as f:
#     json.dump({
#         "total_token": cnt1,
#         "total_gen_dia": cnt2,
#         "total_instruction": cnt3,
#         'average_instruction': cnt3/cnt2,
#         "total_content": cnt4,
#         'average_content': cnt4/cnt2,
#         "total_output": cnt5,
#         'average_output': cnt5/cnt2,
#     }, f, ensure_ascii=False, indent=4)