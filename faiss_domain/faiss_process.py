import faiss
import os
from config import Faiss_Index_Path,Topk
import numpy as np

def list_files_in_directory():
    # 获取指定目录下的所有文件和文件夹名称
    all_entries = os.listdir(Faiss_Index_Path)
    # 过滤出文件（排除文件夹）
    files = [entry for entry in all_entries if os.path.isfile(os.path.join(Faiss_Index_Path, entry))]
    return files


def store_emb(user_id,embeddings):
    # faiss的数据索引是从0开始
    emb_indexs = list_files_in_directory()
    index_path = Faiss_Index_Path+user_id+".index"
    if user_id+".index" in emb_indexs:
        # 向量库已存在时
        index = faiss.read_index(index_path)
        if index.d != embeddings.shape[1]:
            raise ValueError(f"维度不匹配：索引维度 {index.d}，新向量维度 {embeddings.shape[1]}")
        index.add(embeddings)
        faiss.write_index(index, index_path)
    else:
        # 向量库不存在时
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        faiss.write_index(index, index_path)

def simi_search(user_id,query_emb):
    index_path = Faiss_Index_Path+user_id+".index"
    loaded_index = faiss.read_index(index_path)
    if query_emb.ndim == 1:
        query_emb = np.expand_dims(query_emb, axis=0)
    Distance, Index = loaded_index.search(query_emb, Topk)
    # 因为向量索引是从0开始，因此返回的索引要每个都加上1
    return Distance,Index

def scope_search(query_vec,infs_vec):
    # 进行范围搜索
    # 获取向量维度
    d = query_vec.shape[0]
    # 创建 FAISS 索引
    index = faiss.IndexFlatL2(d)  # 使用 L2 距离度量
    # 将 infs_vec 加入索引
    index.add(infs_vec)
    # 查询最相似的向量
    Distance, Index = index.search(query_vec.reshape(1, -1), Topk)
    return Distance,Index