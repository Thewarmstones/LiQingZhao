def get_one_metric(target_metric,lines):
    flag = False
    grade = None

    for i in range(len(lines)):
        if not flag and lines[i].startswith(target_metric):
            flag = True
        elif flag:
            if lines[i].startswith('分数：'):
                grade = lines[i].replace('分数：','')
                if "分" in grade:
                    grade = grade.replace('分','').strip()
            elif lines[i].startswith('理由：'):
                if grade:
                    return {
                        "评分": float(grade),
                        "reason":lines[i].replace('理由：','')
                    }
                else:
                    return 
    return 


def get_bad_turn(lines):
    flag = False
    turn = None
    res = {}
    for i in range(len(lines)):
        if not flag and lines[i].startswith('不符合标准'):
            flag = True
        elif flag:
            if lines[i].startswith('轮次：'):
                turn = lines[i].replace('轮次：','').strip()
                if not turn.isdigit():
                    # print(turn)
                    return res
            elif lines[i].startswith('理由：'):
                if turn:
                    res[int(turn)] = lines[i].replace('理由：','')
                else:
                    return res
    return res


def extract_dialogs(md_text):
    lines = md_text.split('\n')
    metrics = ["内容一致性","对话流畅度","内容覆盖度","时代局限性"]
    res = {}
    for metric in metrics:
        get = get_one_metric(metric,lines)
        if get==None:
            print("wrong")
        else:
            res[metric] = get
    res["bad_turn"] = get_bad_turn(lines)
    return res

import random
from example import Example_dialogue
def ask_allcontent(title,content):
    ## 随机抽取模板嵌套
    exam = random.sample(Example_dialogue,1)[0]
    user_ = exam[0].replace('{{title}}',title)
    assistant_ = exam[1]
    if "{{title}}" in exam[1]:
        assistant_ = exam[1].replace('{{title}}',title)
    assistant_ = assistant_.replace('{{content}}',content)
    return user_,assistant_

import json

with open('poem/finnal_output/judge_fixed_conversation.json','r',encoding='utf-8') as f:
    data = json.load(f)

for i in range(len(data)):
    judge_text = data[i]['judge']
    Q,A = ask_allcontent(data[i]['title'],data[i]['content'])
    data[i]['conversations'][0] = {
        "turn_idx": 1,
        "用户": Q,
        "参考": "",
        "李清照": A
    }
    # data[i]['judge'] = extract_dialogs(judge_text)
with open('poem/finnal_output/judge_fixed_conversation.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)