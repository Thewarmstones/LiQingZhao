import pandas as pd
import jieba
import jieba.posseg as pseg
from collections import defaultdict
import pickle
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class EntityMatcher:
    def __init__(self, entity_df, relationship_df, cache_dir="./cache", top_n=3):
        """
        初始化实体匹配器
        
        参数：
        entity_df: 包含关系信息的DataFrame
        cache_dir: 缓存目录，用于持久化存储
        top_n: 保留的最相关关系数量
        """
        self.entity_df = entity_df
        self.relationship_df = relationship_df
        self.cache_dir = cache_dir
        self.top_n = top_n
        # self.ignore_words = set()
        
        # 创建缓存目录
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        # 指定要保留的词性
        self.valid_pos = {"n", "nr", "nw", "ns", "nt", "nz", "vn", "s", "t"}
        
        # 尝试加载缓存，如果不存在则创建
        self.load_or_create_cache()
        self.add_keywords()
        
        # 创建TF-IDF向量化器，用于计算关系相关度
        self.build_tfidf_model()
        
    def add_keywords(self, file_folder='./keyword'):
        """
        添加实体的关键词
        """
        if os.path.exists(file_folder):
            for file in os.listdir(file_folder):
                if file.endswith(".txt"):
                    file_path = os.path.join(file_folder, file)
                    jieba.load_userdict(file_path)
                    print(f"已添加关键词文件：{file}")
        else:
            print(f"关键词文件夹 {file_folder} 不存在")

    def build_tfidf_model(self):
        """构建TF-IDF模型用于计算相似度"""
        # 收集所有关系描述
        all_descriptions = self.relationship_df['description'].dropna().tolist()
        
        # 如果没有关系描述，则跳过
        if not all_descriptions:
            self.tfidf_vectorizer = None
            self.tfidf_matrix = None
            print("没有找到关系描述，跳过TF-IDF模型构建")
            return
            
        # 创建TF-IDF向量化器
        self.tfidf_vectorizer = TfidfVectorizer(
            tokenizer=lambda x: list(jieba.cut(x)),
            stop_words='english'
        )
        
        # 转换所有描述并拟合向量化器
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_descriptions)
        
        # 创建关系ID到矩阵索引的映射
        self.rel_id_to_index = {}
        valid_idx = 0
        for idx, (_, row) in enumerate(self.relationship_df.iterrows()):
            if pd.notna(row['description']):
                rel_id = f"{row['source']}_{row['target']}"
                self.rel_id_to_index[rel_id] = valid_idx
                valid_idx += 1
                
        print("已构建TF-IDF模型用于计算关系相关度")


    def load_or_create_cache(self):
        """加载或创建缓存文件"""
        cache_file = os.path.join(self.cache_dir, "entity_matcher_cache.pkl")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                self.entity_titles = cache_data.get('entity_titles', [])
                self.entity_words = cache_data.get('entity_words', {})
                self.description_keywords = cache_data.get('description_keywords', {})
                self.description_to_entity = cache_data.get('description_to_entity', {})
                print("已从缓存加载实体匹配数据")
        else:
            # 创建实体标题列表，按长度排序
            self.entity_titles = sorted(self.entity_df['title'].tolist(), key=len, reverse=True)
            
            # 为每个实体创建分词集合
            self.entity_words = {entity: set(jieba.cut(entity)) for entity in self.entity_titles}
            
            # 处理实体描述，提取指定词性的关键词
            self.description_keywords = {}
            self.description_to_entity = {}
            
            for _, row in self.entity_df.iterrows():
                entity_title = row['title']
                description = row['description']
                
                if not isinstance(description, str) or not description.strip():
                    continue
                
                # 分词并保留指定词性的词
                words_with_pos = pseg.cut(description)
                keywords = []
                
                for word, pos in words_with_pos:
                    if pos in self.valid_pos and len(word) > 1:  # 过滤单字词
                        keywords.append(word)
                
                # 按长度排序关键词，优先匹配长词
                keywords = sorted(keywords, key=len, reverse=True)
                self.description_keywords[entity_title] = keywords
                
                # 建立关键词到实体的映射
                for keyword in keywords:
                    if keyword not in self.description_to_entity:
                        self.description_to_entity[keyword] = []
                    self.description_to_entity[keyword].append(entity_title)
            
            # 保存缓存
            with open(cache_file, 'wb') as f:
                cache_data = {
                    'entity_titles': self.entity_titles,
                    'entity_words': self.entity_words,
                    'description_keywords': self.description_keywords,
                    'description_to_entity': self.description_to_entity
                }
                pickle.dump(cache_data, f)
                print("已创建并保存实体匹配缓存")
    
    def extract_entities_from_query(self, query):
        """
        从查询中提取实体
        
        参数：
        query: 用户查询字符串
        
        返回：
        匹配到的实体列表
        """
        # 创建已匹配位置的标记，用于防止重叠匹配
        matched_positions = set()
        entities_in_query = []
        
        # 首先尝试完整匹配（优先匹配完整实体名称）
        for entity in self.entity_titles:
            if entity in query:
                # 检查该实体的位置是否已被匹配
                start_pos = query.find(entity)
                end_pos = start_pos + len(entity)
                
                # 检查是否与已匹配位置重叠
                overlap = False
                for pos in range(start_pos, end_pos):
                    if pos in matched_positions:
                        overlap = True
                        break
                
                if not overlap:
                    # 添加到匹配实体列表
                    entities_in_query.append({
                        "entity": entity,
                        "match_type": "direct_entity_match"
                    })
                    # 标记已匹配位置
                    for pos in range(start_pos, end_pos):
                        matched_positions.add(pos)
        
        # 如果没有直接匹配到实体，尝试分词匹配
        if not entities_in_query:
            query_words = set(jieba.cut(query))
            
            # 对于每个实体，检查其分词结果是否是查询分词结果的子集
            for entity, words in self.entity_words.items():
                # 计算交集比例
                if words and query_words:
                    intersection = words.intersection(query_words)
                    if len(intersection) / len(words) >= 0.7:  # 如果70%以上的词匹配
                        entities_in_query.append({
                            "entity": entity,
                            "match_type": "word_match",
                            "matched_words": list(intersection)
                        })
        
        return entities_in_query
    
    def extract_entities_from_description(self, query):
        """
        通过描述关键词匹配实体
        
        参数：
        query: 用户查询字符串
        
        返回：
        通过描述关键词匹配到的实体列表
        """
        matched_positions = set()
        matched_entities = []
        
        # 按照关键词长度优先匹配
        all_keywords = sorted(self.description_to_entity.keys(), key=len, reverse=True)
        
        for keyword in all_keywords:
            if keyword in query:
                # 检查该关键词的位置是否已被匹配
                start_pos = query.find(keyword)
                end_pos = start_pos + len(keyword)
                
                # 检查是否与已匹配位置重叠
                overlap = False
                for pos in range(start_pos, end_pos):
                    if pos in matched_positions:
                        overlap = True
                        break
                
                if not overlap:
                    # 获取包含该关键词的实体
                    entities = self.description_to_entity[keyword]
                    for entity in entities:
                        matched_entities.append({
                            "entity": entity,
                            "keyword": keyword,
                            "match_type": "description_keyword_match"
                        })
                    
                    # 标记已匹配位置
                    for pos in range(start_pos, end_pos):
                        matched_positions.add(pos)
        
        # 如果没有直接匹配到关键词，尝试分词匹配
        if not matched_entities:
            query_words = set(jieba.cut(query))
            
            # 对于每个关键词，检查是否在查询分词结果中
            for keyword in all_keywords:
                keyword_words = set(jieba.cut(keyword))
                if keyword_words and query_words:
                    intersection = keyword_words.intersection(query_words)
                    if len(intersection) / len(keyword_words) >= 0.7:  # 如果70%以上的词匹配
                        entities = self.description_to_entity[keyword]
                        for entity in entities:
                            matched_entities.append({
                                "entity": entity,
                                "keyword": keyword,
                                "match_type": "description_word_match",
                                "matched_words": list(intersection)
                            })
        
        return matched_entities
    
    def get_entity_details(self, entity_name):
        """获取实体的详细信息"""
        entity_data = self.entity_df[self.entity_df['title'] == entity_name]
        if len(entity_data) > 0:
            return {
                "title": entity_name,
                "description": entity_data['description'].values[0]
            }
        return {"title": entity_name, "description": ""}
    
    def get_entity_relationships(self, entity_name, query=None):
        """
        获取实体的关系信息，并根据查询计算相关度
        
        参数：
        entity_name: 实体名称
        query: 用户查询，用于计算关系相关度
        
        返回：
        按相关度排序的关系列表
        """
        # 查找以该实体为源或目标的关系
        source_relations = self.relationship_df[self.relationship_df['source'] == entity_name]
        target_relations = self.relationship_df[self.relationship_df['target'] == entity_name]
        
        relationships = []
        
        # 处理源关系
        for _, rel in source_relations.iterrows():
            relationships.append({
                "source": rel['source'],
                "target": rel['target'],
                "description": rel['description'],
                "direction": "outgoing"
            })
        
        # 处理目标关系
        for _, rel in target_relations.iterrows():
            relationships.append({
                "source": rel['source'],
                "target": rel['target'],
                "description": rel['description'],
                "direction": "incoming"
            })
        
        # 如果有查询且有TF-IDF模型，计算关系相关度
        if query and self.tfidf_vectorizer and len(relationships) > 0:
            # 将查询转换为TF-IDF向量
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # 计算每个关系与查询的相似度
            for rel in relationships:
                rel_id = f"{rel['source']}_{rel['target']}"
                if rel_id in self.rel_id_to_index:
                    idx = self.rel_id_to_index[rel_id]
                    rel_vector = self.tfidf_matrix[idx]
                    similarity = cosine_similarity(query_vector, rel_vector)[0][0]
                    rel['relevance'] = float(similarity)
                else:
                    rel['relevance'] = 0.0
            
            # 按相关度排序
            relationships = sorted(relationships, key=lambda x: x.get('relevance', 0), reverse=True)
            
            # 只保留前top_n个关系
            if self.top_n > 0:
                relationships = relationships[:self.top_n]
        
        return relationships
    
    def extract_all(self, query, max_results=10):
        """
        综合提取查询中的实体和关系，限制返回结果数量
        
        参数：
        query: 用户查询字符串
        max_results: 最大返回结果数量，默认为10
        
        返回：
        包含匹配实体和关系的字典
        """
        # 从实体名称直接匹配
        direct_matches = self.extract_entities_from_query(query)
        
        # 从描述关键词匹配
        description_matches = self.extract_entities_from_description(query)
        
        # 合并结果并去重
        all_matches = direct_matches + description_matches
        
        # 为匹配的实体添加详细信息和关系
        result = []
        processed_entities = set()
        
        # 限制处理的匹配数量
        count = 0
        for match in all_matches:
            if count >= max_results:
                break
                
            entity_name = match["entity"]
            
            # 跳过已处理的实体
            if entity_name in processed_entities:
                continue
            
            processed_entities.add(entity_name)
            count += 1
            
            # 获取实体详情
            entity_details = self.get_entity_details(entity_name)
            
            # 获取实体关系，并按与查询的相关度排序
            entity_relationships = self.get_entity_relationships(entity_name, query)
            
            # 收集所有相关实体
            related_entities = []
            for rel in entity_relationships:
                other_entity = rel['target'] if rel['source'] == entity_name else rel['source']
                if other_entity not in processed_entities:
                    related_entities.append(other_entity)
            
            # 获取相关实体的详情
            related_entity_details = []
            for related_entity in related_entities:
                related_entity_details.append(self.get_entity_details(related_entity))
            
            result.append({
                "entity": entity_details,
                "match_type": match.get("match_type"),
                "keyword": match.get("keyword", ""),
                "matched_words": match.get("matched_words", []),
                "relationships": entity_relationships,
                "related_entities": related_entity_details
            })
        
        return {
            "matches": result,
            "match_count": len(result)
        }
    def format_results_as_text(self, results):
        """
        将实体匹配结果格式化为易读的文本
        
        参数：
        results: extract_all 函数返回的结果字典
        
        返回：
        格式化后的文本字符串
        """
        if results["match_count"] == 0:
            return "未匹配到实体。"
        
        text_output = []
        text_output.append(f"保留 {results['match_count']} 个匹配实体：\n")
        
        for i, match in enumerate(results["matches"], 1):
            entity = match["entity"]
            entity_title = entity["title"]
            entity_desc = entity["description"] if entity["description"] else "无描述"
            
            text_output.append(f"{i}. 实体：{entity_title}")
            text_output.append(f"   描述：{entity_desc}")
            text_output.append(f"   匹配类型：{match['match_type']}")
            
            if match.get("keyword"):
                text_output.append(f"   匹配关键词：{match['keyword']}")
            
            if match.get("matched_words"):
                text_output.append(f"   匹配词：{', '.join(match['matched_words'])}")
            
            # 添加关系信息
            if match["relationships"]:
                text_output.append("\n   相关关系：")
                for j, rel in enumerate(match["relationships"], 1):
                    source = rel["source"]
                    target = rel["target"]
                    desc = rel["description"] if rel["description"] else "无描述"
                    
                    text_output.append(f"   {j}. {source}之于{target}：{desc}")
                    
                    # 如果有相关度信息，也显示出来
                    if "relevance" in rel:
                        relevance = rel["relevance"]
                        text_output.append(f"      相关度：{relevance:.4f}")
            else:
                text_output.append("\n   无相关关系")
            
            # 添加相关实体信息
            if match["related_entities"]:
                text_output.append("\n   相关实体：")
                for j, rel_entity in enumerate(match["related_entities"], 1):
                    rel_title = rel_entity["title"]
                    rel_desc = rel_entity["description"] if rel_entity["description"] else "无描述"
                    
                    text_output.append(f"   {j}. {rel_title}：{rel_desc}")
            else:
                text_output.append("\n   无相关实体")
            
            # 添加分隔线
            if i < results["match_count"]:
                text_output.append("\n" + "-" * 80 + "\n")
        
        return "\n".join(text_output)


INPUT_DIR = "./data"
ENTITY_TABLE = "entities"
RELATIONSHIP_TABLE = "relationships"

## 实体
entity_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")
print(f"Entity count: {len(entity_df)}")
## 关系
relationship_df = pd.read_parquet(f"{INPUT_DIR}/{RELATIONSHIP_TABLE}.parquet")
print(f"Relationship count: {len(relationship_df)}")

# entity_df.head(3),relationship_df.head(3)

test = EntityMatcher(entity_df,relationship_df)


while True:
    query = input("请输入查询：")
    result = test.extract_all(query)
    print(result)
    print()
    print(test.format_results_as_text(result))