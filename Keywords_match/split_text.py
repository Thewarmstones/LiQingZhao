import jieba
ignore_set = set()
import re,os
import json
import random

with open('./keyword/ignoreword.txt','r',encoding='utf-8') as f:
    for line in f.readlines():
        ignore_set.add(line.strip())

with open('./keyword/show.txt','r',encoding='utf-8') as f:
    care_word = [line.split('\t')[0] for line in f.readlines() if line.split('\t')[0] not in ignore_set]
    care_word = list(set(care_word))
    print(len(care_word))
    exit()
for file in ['./text_data/李清照-杨雨(分析部分).txt','./text_data/李清照-杨雨(身世部分).txt']:
    with open(file,'r',encoding='utf-8') as f:
        text = f.readlines()
    # print(data)
    print(care_word)
    for para in text:
        para = para.strip()
        if para=='':
            continue
        # print(para)
        for word in care_word:
            if word in para:
                with open('../../src_data/split_byword_text/'+word+'.txt','a',encoding='utf-8') as f:
                    f.write(para+'\n')

# print(len(data))