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
        self.entity_df = entity_df
        self.relationship_df = relationship_df
        self.cache_dir = cache_dir
        self.top_n = top_n

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        self.valid_pos = {"n", "nr", "nw", "ns", "nt", "nz", "vn", "s", "t","m"}

        self.load_or_create_cache()
        self.add_keywords()

        self.build_tfidf_model()

    # add_keywords 和 build_tfidf_model 方法保持不变
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
        cache_file = os.path.join(self.cache_dir, "entity_matcher_cache.pkl")

        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
                self.entity_titles = cache_data.get('entity_titles', [])
                self.entity_words = cache_data.get('entity_words', {})
                print("已从缓存加载实体匹配数据")
        else:
            self.entity_titles = sorted(self.entity_df['title'].tolist(), key=len, reverse=True)

            self.entity_words = {}
            for entity in self.entity_titles:
                words = pseg.cut(entity)
                self.entity_words[entity] = set(word for word, pos in words if pos in self.valid_pos)

            with open(cache_file, 'wb') as f:
                cache_data = {
                    'entity_titles': self.entity_titles,
                    'entity_words': self.entity_words,
                }
                pickle.dump(cache_data, f)
                print("已创建并保存实体匹配缓存")

    def extract_entities_from_query(self, query):
        matched_positions = set()
        entities_in_query = []

        for entity in self.entity_titles:
            if entity in query:
                start_pos = query.find(entity)
                end_pos = start_pos + len(entity)

                overlap = False
                for pos in range(start_pos, end_pos):
                    if pos in matched_positions:
                        overlap = True
                        break

                if not overlap:
                    entities_in_query.append({
                        "entity": entity,
                        "match_type": "direct_entity_match"
                    })
                    for pos in range(start_pos, end_pos):
                        matched_positions.add(pos)

        if not entities_in_query:
            query_words = set()
            long_words = set()
            for word, pos in pseg.cut(query):
                if pos in self.valid_pos:
                    query_words.add(word)
                    if len(word) > 2:
                        long_words.add(word)

            for entity, words in self.entity_words.items():
                # print(entity, query_words)
                if words and query_words:
                    intersection = words.intersection(query_words)
                    involve = False
                    for word in long_words:
                        if word in entity:
                            involve = True
                            break
                    if involve or len(intersection) / len(words) >= 0.7:
                        entities_in_query.append({
                            "entity": entity,
                            "match_type": "word_match",
                            "matched_words": list(intersection)
                        })

        return entities_in_query


    def get_entity_details(self, entity_name):
        entity_data = self.entity_df[self.entity_df['title'] == entity_name]
        if len(entity_data) > 0:
            return {
                "title": entity_name,
                "description": entity_data['description'].values[0]
            }
        return {"title": entity_name, "description": ""}

    def get_entity_relationships(self, entity_name, query=None):
        source_relations = self.relationship_df[self.relationship_df['source'] == entity_name]
        target_relations = self.relationship_df[self.relationship_df['target'] == entity_name]

        relationships = []
        related_entities = set()

        for _, rel in source_relations.iterrows():
            relationships.append({
                "source": rel['source'],
                "target": rel['target'],
                "description": rel['description'],
                "direction": "outgoing"
            })
            related_entities.add(rel['target'])

        for _, rel in target_relations.iterrows():
            relationships.append({
                "source": rel['source'],
                "target": rel['target'],
                "description": rel['description'],
                "direction": "incoming"
            })
            related_entities.add(rel['source'])

        if query and self.tfidf_vectorizer and len(relationships) > 0:
            query_vector = self.tfidf_vectorizer.transform([query])

            for rel in relationships:
                rel_id = f"{rel['source']}_{rel['target']}"
                if rel_id in self.rel_id_to_index:
                    idx = self.rel_id_to_index[rel_id]
                    rel_vector = self.tfidf_matrix[idx]
                    similarity = cosine_similarity(query_vector, rel_vector)[0][0]
                    rel['relevance'] = float(similarity)
                else:
                    rel['relevance'] = 0.0

            relationships = sorted(relationships, key=lambda x: x.get('relevance', 0), reverse=True)

            # if self.top_n > 0:
            #     relationships = relationships[:self.top_n]
            relationships = relationships

        return relationships, list(related_entities)

    def extract_all(self, query, max_results=10):
        direct_matches = self.extract_entities_from_query(query)

        result = []
        processed_entities = set()

        count = 0
        for match in direct_matches:
            if count >= max_results:
                break

            entity_name = match["entity"]

            if entity_name in processed_entities:
                continue

            processed_entities.add(entity_name)
            count += 1

            entity_details = self.get_entity_details(entity_name)

            entity_relationships, related_entities = self.get_entity_relationships(entity_name, query)

            related_entity_details = []
            for related_entity in related_entities:
                if related_entity not in processed_entities:
                    related_entity_details.append(self.get_entity_details(related_entity))
                    processed_entities.add(related_entity)

            result.append({
                "entity": entity_details,
                "match_type": match.get("match_type"),
                "matched_words": match.get("matched_words", []),
                "relationships": entity_relationships,
                "related_entities": related_entity_details
            })

        return {
            "matches": result,
            "match_count": len(result)
        }

    def format_results_as_text(self, results):
        if results["match_count"] == 0:
            return ""

        text_output = []

        for i, match in enumerate(results["matches"], 1):
            entity = match["entity"]
            entity_title = entity["title"]
            entity_desc = entity["description"] if entity["description"] else ""

            text_output.append(f"实体：{entity_title}--{entity_desc}")



            # 实体关系
            if match["relationships"]:
                for j, rel in enumerate(match["relationships"], 1):
                    source = rel["source"]
                    target = rel["target"]
                    desc = rel["description"] if rel["description"] else ""
                    text_output.append(f"   {j}. {source}之于{target}：{desc}")

            if i < results["match_count"]:
                text_output.append("-" * 80)

        return "\n".join(text_output)


# INPUT_DIR = "./data"
# ENTITY_TABLE = "entities"
# RELATIONSHIP_TABLE = "relationships"
#
# ## 实体
# entity_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")
# print(f"Entity count: {len(entity_df)}")
# ## 关系
# relationship_df = pd.read_parquet(f"{INPUT_DIR}/{RELATIONSHIP_TABLE}.parquet")
# print(f"Relationship count: {len(relationship_df)}")
#
# # entity_df.head(3),relationship_df.head(3)
#
# test = EntityMatcher(entity_df,relationship_df)
#
#
# while True:
#     query = input("请输入查询：")
#     result = test.extract_all(query)
#     print(test.format_results_as_text(result))
