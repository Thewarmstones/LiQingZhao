import subprocess

def graphSearch(_query):
    # 定义命令参数
    command = [
        "graphrag", "query",
        "--root", "/home/zkp/LiQingZhao/resources/Database/graphRag",
        "--method", "local",
        "--query", _query
    ]

    target = "Local Search Response:\n"


    # 执行命令并捕获输出
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True).stdout
        index = result.find(target)
        if index != -1:  # 如果找到目标字符串
            result = result[index + len(target):].strip()  # 切片获取目标字符串后面的内容
        else:
            result = ""
        # print(result)  # 打印标准输出
    except subprocess.CalledProcessError as e:
        result = ""
    return result

# search("李清照在什么时候写得声声慢？")
# print("--------------------------------------------------")

# from graphrag import query
# print(query("《声声慢》的全文是?"))
# import os

# import pandas as pd
# import tiktoken

# from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey
# from graphrag.query.indexer_adapters import (
#     read_indexer_covariates,
#     read_indexer_entities,
#     read_indexer_relationships,
#     read_indexer_reports,
#     read_indexer_text_units,
# )
# from graphrag.query.input.loaders.dfs import (
#     store_entity_semantic_embeddings,
# )
# from graphrag.query.llm.oai.chat_openai import ChatOpenAI
# from graphrag.query.llm.oai.embedding import OpenAIEmbedding
# from graphrag.query.llm.oai.typing import OpenaiApiType
# from graphrag.query.question_gen.local_gen import LocalQuestionGen
# from graphrag.query.structured_search.local_search.mixed_context import (
#     LocalSearchMixedContext,
# )
# from graphrag.query.structured_search.local_search.search import LocalSearch
# from graphrag.vector_stores.lancedb import LanceDBVectorStore