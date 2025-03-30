import jieba.posseg as pseg
import jieba
import re,os
import json
import random
from collections import defaultdict
import os

# 设置工作目录为当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

class FullTextRAGSystem:
    def __init__(self, text_file=None):
        self.text_file_list = text_file
        self.inverted_index = defaultdict(list)  # 倒排索引
        self.sentences = []  # 文本分割后的句子
        self.line_sentences = [] 
        self.pos_tags = {"n", 'nr' , "ns", "nt", "nz"}  # 关注的词性表
        self.full_sentence_tags = {"r","v"}
        self.query_word_set = set()
        self.ignore_words = self.get_ignore_word()
        jieba.load_userdict('./keyword/fix_keyword.txt')
        jieba.load_userdict('./keyword/add_keyword.txt')
        jieba.load_userdict('./keyword/add_poem_keyword.txt')
        # jieba.load_userdict('./keyword/show_.txt')
        
        
    def get_ignore_word(self):
        ignore_set = set()
        
        with open('./keyword/ignoreword.txt','r',encoding='utf-8') as f:
            for line in f.readlines():
                ignore_set.add(line.strip())
        return ignore_set  
          
    # 构建倒排索引
    def build_inverted_index(self):
        text = self.load_text()
        # 使用正则分割句子
        self.sentences = [s.strip() for s in re.split(r'[。！？]', text) if s.strip()]

        for sentence in self.sentences+self.line_sentences:
            words_with_pos = pseg.cut(sentence)  # 使用 jieba 进行词性标注
            unique_words = set(word for word, flag in words_with_pos if flag in self.pos_tags and word not in self.ignore_words and len(word)>1)  # 筛选词性
            for word in unique_words:
                self.inverted_index[word].append(sentence)

    # 处理用户查询
    def process_query(self,history, query, top_n=None):
        # 使用 jieba 分词并标注词性
        query_words_with_pos = list(pseg.cut(query))
        self.query_word_set = set()
        check = [False,False] # 主谓检查
        for word, flag in query_words_with_pos:
            # print(word,flag)
            if flag in self.pos_tags:# 筛选词性
                if word in self.inverted_index:
                    self.query_word_set.add(word)
                check[0] = True
            elif flag=='v':
                check[1] = True
            elif flag=='r':
                check[0] = True
            # print(word,flag)
        user_history = self.is_independent_query(history,query,check)

        sentence_scores = defaultdict(int)
        for word in self.query_word_set:
            for sentence in self.inverted_index[word]:
                sentence_scores[sentence] += 1

        # 根据匹配到的分词数量对句子排序
        sorted_sentences = sorted(
            sentence_scores.items(),
            key=lambda x: x[1],  # 按匹配分词数量排序
            reverse=True
        )
        result = []
        for sentence, score in sorted_sentences[:top_n]:
            if score>1:
                result.append(sentence)
                # print(result)
            else:# 每个独立分词都取若干个做补充
                get = (top_n-len(result))//len(self.query_word_set)+1
                for word in self.query_word_set:
                    result+=random.sample(self.inverted_index[word],min(get,len(self.inverted_index[word])))
                result = list(set(result))  # 去重
                break
        return self.query_word_set,result
        # return user_history,result # 如果指定了 top_n，则只返回前 top_n 个结果
    

# 你是如何做到与张汝州离婚的？

    # 加载文本内容
    def load_text(self):
        if self.text_file_list=="":
            with open(self.text_file_list, 'r', encoding='utf-8') as f:
                text = f.read()
            return text
        text = ""
        file_List = os.listdir(self.text_file_list)
        if 'addline' in file_List:
            line_input_folder = os.path.join(self.text_file_list,'addline')
            for file in os.listdir(line_input_folder):
                if not file.endswith('.txt'):
                    continue
                with open(os.path.join(line_input_folder,file), 'r', encoding='utf-8') as f:
                    self.line_sentences += [line.strip() for line in f.readlines() if line.strip()]
        for file_name in file_List:
            if not file_name.endswith('.txt'):
                continue
            path = os.path.join(self.text_file_list,file_name)
            with open(path, 'r', encoding='utf-8') as f:
                text += f.read()
        return text
    # 存储倒排索引到文件
    def save_to_file(self, output_file):
        # 将数据转换为可序列化的格式
        data = {
            "inverted_index": {k: v for k, v in self.inverted_index.items()},  # 倒排索引直接保存
            "sentences": self.sentences
        }
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    # 辅助函数：从文件加载倒排索引
    def load_from_file(self, input_file):
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 加载倒排索引和句子
        self.inverted_index = defaultdict(list, data["inverted_index"])
        self.sentences = data["sentences"]


    def is_independent_query(self,history,query,check):
        """
        检测 query 是否为独立对话。
        :param query: 输入的句子
        :return: True（独立对话）或 False（非独立对话）
        """
        # print(check)
        if check[0] and check[1] and len(query)>13:
            return self.check_need_history(history)
        return True

    def check_need_history(self,history):
        """
        最终判断是否需要参考历史
        """
        for word, flag in pseg.cut(history):
            if word in self.query_word_set:
                return True
        return False