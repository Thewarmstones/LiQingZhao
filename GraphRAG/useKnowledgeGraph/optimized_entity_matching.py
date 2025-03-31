import pandas as pd
import jieba
from collections import defaultdict
import re


class EntityMatcher:
    def __init__(self, entity_df, relationship_df):
        """
        初始化实体匹配器
        
        参数：
        entity_df: 包含实体信息的DataFrame
        """
        self.entity_df = entity_df
        self.entity_titles = sorted(entity_df['title'].tolist(), key=len, reverse=True)
        self.entity_words = {entity: set(jieba.cut(entity)) for entity in self.entity_titles}
        self.relationship_df = relationship_df
    
    def extract_entities_and_relationships(self, query):
        """
        优化的实体匹配和关系提取函数
        
        解决问题：
        1. 防止子字符串匹配问题（如"金华"和"金"同时匹配）
        2. 优先保留已有实体间的关系
        
        参数：
        query: 用户查询字符串
        relationship_df: 包含关系信息的DataFrame
        
        返回：
        包含匹配实体及其关系的列表
        """
        # 对查询进行分词
        query_words = set(jieba.cut(query))
        
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
                    entities_in_query.append(entity)
                    # 标记已匹配位置
                    for pos in range(start_pos, end_pos):
                        matched_positions.add(pos)
        
        # 如果没有找到完整匹配，尝试使用分词结果进行匹配
        if not entities_in_query:
            # 基于分词结果匹配（使用初始化时已经处理好的实体分词结果）
            for entity, words in self.entity_words.items():
                # 如果实体分词结果是查询分词结果的子集，则认为匹配
                if words.issubset(query_words):
                    entities_in_query.append(entity)
        
        if not entities_in_query:
            print("未在 query 中找到匹配的实体。")
            return None
        
        # 获取匹配实体的 description
        matched_entities = self.entity_df[self.entity_df['title'].isin(entities_in_query)][['title', 'description']]
        matched_entities_dict = dict(zip(matched_entities['title'], matched_entities['description']))
        
        # 创建关系的快速查找表
        relationships_grouped = defaultdict(list)
        for _, row in self.relationship_df.iterrows():
            relationships_grouped[row['source']].append({
                "source": row['source'],
                "target": row['target'],
                "description": row['description']
            })
            relationships_grouped[row['target']].append({
                "source": row['source'],
                "target": row['target'],
                "description": row['description']
            })
        
        # 构建结果，优先保留已有实体间的关系
        result = []
        for entity in entities_in_query:
            entity_description = matched_entities_dict.get(entity, "")
            
            # 获取与该实体相关的所有关系
            related_relationships = relationships_grouped.get(entity, [])
            
            # 优先保留与其他匹配实体的关系
            prioritized_relationships = []
            other_relationships = []
            
            for rel in related_relationships:
                # 检查关系的另一端是否也在匹配的实体中
                other_entity = rel['target'] if rel['source'] == entity else rel['source']
                if other_entity in entities_in_query:
                    prioritized_relationships.append(rel)
                else:
                    other_relationships.append(rel)
            
            # 合并关系列表，优先关系在前
            final_relationships = prioritized_relationships + other_relationships
            
            result.append({
                "entity": entity,
                "entity_description": entity_description,
                "relationships": final_relationships
            })
        
        return result


INPUT_DIR = "../graphRag/output"
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
    query = input()
    response = test.extract_entities_and_relationships(query)
    print(response)