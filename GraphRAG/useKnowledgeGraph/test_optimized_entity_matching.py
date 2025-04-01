import unittest
import pandas as pd
import sys
import os

# 导入要测试的模块
from optimized_entity_matching import extract_entities_and_relationships_optimized, get_entity_by_name

class TestOptimizedEntityMatching(unittest.TestCase):
    
    def setUp(self):
        """测试前的准备工作，创建测试数据"""
        # 设置数据路径
        self.input_dir = "../graphRag/output"
        self.entity_table = "entities"
        self.relationship_table = "relationships"
        
        # 读取实体和关系数据
        try:
            self.entity_df = pd.read_parquet(f"{self.input_dir}/{self.entity_table}.parquet")
            self.relationship_df = pd.read_parquet(f"{self.input_dir}/{self.relationship_table}.parquet")
            print(f"成功加载数据: 实体数量 {len(self.entity_df)}, 关系数量 {len(self.relationship_df)}")
        except Exception as e:
            print(f"加载数据失败: {e}")

   
    
    def test_input_validation(self):
        """测试输入验证功能"""
        # 测试空查询
        result = extract_entities_and_relationships_optimized("", self.entity_df, self.relationship_df)
        self.assertIsNone(result)
        
        # 测试None查询
        result = extract_entities_and_relationships_optimized(None, self.entity_df, self.relationship_df)
        self.assertIsNone(result)
        
        # 测试None实体数据
        result = extract_entities_and_relationships_optimized("李清照", None, self.relationship_df)
        self.assertIsNone(result)
        
        # 测试None关系数据
        result = extract_entities_and_relationships_optimized("李清照", self.entity_df, None)
        self.assertIsNone(result)
    
    def test_substring_matching(self):
        """测试子字符串匹配问题（如"金华"和"金"同时匹配）"""
        # 查询中同时包含"金华"和"金"
        query = "金华是一个盛产黄金的地方"
        result = extract_entities_and_relationships_optimized(query, self.entity_df, self.relationship_df)
        
        # 应该只匹配"金华"而不是"金