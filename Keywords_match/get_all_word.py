# from build import RAGSystem
from build2 import FullTextRAGSystem
import re
import jieba.posseg as pseg
import os
from tqdm import tqdm
rag_system = FullTextRAGSystem("./text_data" )

pos_tags = {"n", "nr" , "nw", "ns", "nt", "nz","vn","s","a","an","t"}

output_folder = "./partOfSpeech/tags"
text = rag_system.load_text()

for tag in pos_tags:
    output_subfolder = os.path.join(output_folder, tag)
    sentences = [s.strip() for s in re.split(r'[。！？]', text) if s.strip()]
    unique_words = set()
    for sentence in tqdm(sentences):
        words_with_pos = pseg.cut(sentence)  # 使用 jieba 进行词性标注
        for word, flag in words_with_pos:
            if flag == tag:
                unique_words.add(word)
    with open(output_subfolder+'.txt','w',encoding='utf-8') as f:
        f.write('\n'.join(list(unique_words)))
    print(tag,'over!')
print('all finished!')
# while True:
#     query = input("query：")
#     results = rag_system.process_query(query)
#     print("查询结果：",'\n'.join(results))


