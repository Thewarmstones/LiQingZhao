# from build import RAGSystem
from build2 import FullTextRAGSystem
import jieba.posseg as pseg
# 示例用法
if __name__ == "__main__":
    # keyword_file = "./keyword/all_keyword.txt"  # 关键词文件路径
    text_file = "./text_data"         # 文本文件路径
    # output_file2 = "./storage/test2/inverted_index.json"  # 倒排索引存储文件路径

    # rag_system = RAGSystem(keyword_file, text_file)

    # # 加载关键词
    # rag_system.load_keywords()

    # # 构建倒排索引
    # rag_system.build_inverted_index()

    # # 存储倒排索引到文件
    # rag_system.save_to_file(output_file2)

    # import re

    # # 正则表达式
    # pattern = r'“([^”]*)”'
    # rag_system = FullTextRAGSystem(text_file=text_file)
    # # 查找所有匹配项
    # matches = [word for word in re.findall(pattern, rag_system.load_text()) if len(word)<8 and len(word)>1]
    # matches = list(set(matches))
    # # 输出结果
    # print(matches)
    # with open('/home/zkp/LiQingZhao/resources/Database/Keywords_match/keyword/add_keyword.txt','w',encoding='utf-8') as f:
    #     f.write(' 200 nz\n'.join(matches))
    # exit()
    
    rag_system = FullTextRAGSystem(text_file=text_file)
    rag_system.build_inverted_index()
    output_file3 = "./storage/inverted_index.json"  # 倒排索引存储文件路径
    rag_system.save_to_file(output_file3)
    rag_system = FullTextRAGSystem()
    rag_system.load_from_file("./storage/inverted_index.json")
    results = rag_system.process_query("",'init_start', top_n=5)  # 返回前 5 个最相关的句子
    print('over!Please start.')
    while True:
        query = input()
        for word,flag in pseg.cut(query):
            print(word,flag)
        results = rag_system.process_query("",query, top_n=5)  # 返回前 5 个最相关的句子
        print(results)