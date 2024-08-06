from FlagEmbedding import FlagModel
from config import *
from faiss_domain.faiss_process import store_emb
import numpy as np

import os
os.environ['CUDA_VISIBLE_DEVICES'] = "0"

def embedding_query(data):
    # data:[]
    model = FlagModel(Embedding_Model_Path, 
                    query_instruction_for_retrieval="为这个句子生成表示以用于检索相关文章：",
                    use_fp16=True)
    # 向量化
    embeddings = model.encode(data)
    embeddings = np.array(embeddings, dtype='float32')
    return embeddings

def text_2_vec(user_id,data:list):
    # 对对话数据进行处理
    # dialogue_id为数据
    # data形式为：[[dialogue_id,user,assis],[],[]]
    user_ = []
    for i in range(len(data)):
        user_.append(data[i][1])
    embeddings = embedding_query(user_)
    # 存储向量
    store_emb(user_id,embeddings)

def inf_2_vec(user_id,data):
    # 对总结的信息进行提取
    user_ = []
    for i in range(len(data)):
        user_.append(data[i])
    embeddings = embedding_query(user_)
    # 存储向量
    store_emb(user_id,embeddings)



