import os

# 数据库存储根目录
Database_Root_Path = "/data/hongzhili/db_domain/"
# 向量模型地址
Embedding_Model_Path = "/home/kuaipan/model/bgelarge/bge-large-zh-v1.5"
# faiss索引根目录
Faiss_Index_Path = "/home/kuaipan/memdb/faiss_domain/faiss_index/"
# Top K
Topk = 3
# openai 跳板机地址
Base_Url='http://8.209.215.15/api/openai/v1'
# openai key 推送git时要将key删掉
Api_Key=""



# 获取数据库地址
def get_db_path(db_name):
    return Database_Root_Path+db_name+".db"
# 服务于内存数据库初始化
def get_db_inf():
    db_paths = {}
    directory_path = "/data/hongzhili/db_domain/"
    files_and_folders = os.listdir(directory_path)
    for i in range(len(files_and_folders)):
        db_paths[files_and_folders[i].split(".")[0]] = directory_path+files_and_folders[i]
    return db_paths