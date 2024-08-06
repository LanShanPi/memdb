# from FlagEmbedding import FlagModel
# from config import *
# from faiss_domain.faiss_process import store_emb
# import numpy as np

# import os
# os.environ['CUDA_VISIBLE_DEVICES'] = "0"

# class EmbeddingService:
#     def __init__(self,):
#         self.model = FlagModel(Embedding_Model_Path, 
#                                query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
#                                use_fp16=True)

#     def embedding_query(self,data):
#         embeddings = self.model.encode(data)
#         embeddings = np.array(embeddings, dtype='float32')
#         return embeddings 

#     def text_2_vec(self,user_id,data:list):
#         # 对对话数据进行处理
#         # dialogue_id为数据
#         # data形式为：[[dialogue_id,user,assis],[],[]]
#         user_ = []
#         for i in range(len(data)):
#             user_.append(data[i][1])
#         embeddings = self.embedding_query(user_)
#         # 存储向量
#         store_emb(user_id,embeddings)

#     def inf_2_vec(self,user_id,data):
#         # 对总结的信息进行提取
#         user_ = []
#         for i in range(len(data)):
#             user_.append(data[i])
#         embeddings = self.embedding_query(user_)
#         # 存储向量
#         store_emb(user_id,embeddings)


import asyncio
from FlagEmbedding import FlagModel
from config import *
from faiss_domain.faiss_process import store_emb
import numpy as np
import os

os.environ['CUDA_VISIBLE_DEVICES'] = "0"

class EmbeddingService:
    def __init__(self):
        self.model = FlagModel(
            Embedding_Model_Path, 
            query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
            use_fp16=True
        )

    async def embedding_query(self, data):
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, self.model.encode, data)
        embeddings = np.array(embeddings, dtype='float32')
        return embeddings

    async def text_2_vec(self, user_id, data: list):
        loop = asyncio.get_event_loop()
        user_ = [entry[1] for entry in data]  # 提取用户对话内容
        embeddings = await self.embedding_query(user_)
        await loop.run_in_executor(None, store_emb, user_id, embeddings)  # 异步存储向量

    async def inf_2_vec(self, user_id, data):
        loop = asyncio.get_event_loop()
        user_ = [entry for entry in data]  # 提取信息内容
        embeddings = await self.embedding_query(user_)
        await loop.run_in_executor(None, store_emb, user_id, embeddings)  # 异步存储向量


