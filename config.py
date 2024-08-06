import os

# 数据库存储根目录
Database_Root_Path = "/home/kuaipan/memdb/db_domain/"
# 向量模型地址
Embedding_Model_Path = "/home/kuaipan/model/bgelarge/bge-large-zh-v1.5"
# faiss索引根目录
Faiss_Index_Path = "/home/kuaipan/memdb/faiss_domain/faiss_index/"
# Top K
Topk = 3

# 获取数据库地址
def get_db_path(db_name):
    return Database_Root_Path+db_name+".db"

# # 数据库路径
# db_paths = {
#     "birthdate": "/home/kuaipan/memdb/db_domain/birthdate.db",
#     "dialogue": "/home/kuaipan/memdb/db_domain/dialogue.db",
#     "information": "/home/kuaipan/memdb/db_domain/information.db",
#     "paipan_data_book": "/home/kuaipan/memdb/db_domain/paipan_data_book.db",
# }


def get_db_inf():
    db_paths = {}
    directory_path = "/home/kuaipan/memdb/db_domain/"
    files_and_folders = os.listdir(directory_path)
    for i in range(len(files_and_folders)):
        db_paths[files_and_folders[i].split(".")[0]] = directory_path+files_and_folders[i]
    return db_paths