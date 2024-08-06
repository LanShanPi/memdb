import sqlite3
from typing import List, Any, Dict
import os
from config import *
import logging
from embd_domain.emb_text import *
from faiss_domain.faiss_process import *
from db_init import get_memory_db
# 使用上下文管理器with sqlite3.connect(db_path) as conn：上下文管理器可以自动管理连接的开启和关闭，防止数据锁定
# conn.execute('PRAGMA journal_mode=WAL') 将 SQLite 的日记模式（journal mode）设置为 WAL（Write-Ahead Logging）
# 提升并发性能，减少磁盘I/O操作，提高写入速度
# conn.execute('PRAGMA wal_checkpoint') 将 WAL 文件的内容合并回主数据库文件

#################################################################
# 数据库数据表创、删
def database_exists(db_name:str) -> bool:
    db_path = get_db_path(db_name)
    return os.path.exists(db_path)

def table_exists(db_name:str,table_name:str) -> bool:
    db_path = get_db_path(db_name)
    with sqlite3.connect(db_path) as conn:
        conn.execute('PRAGMA journal_mode=WAL')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return cursor.fetchone() is not None

    
def create_database(db_name: str):
    db_path = get_db_path(db_name)
    if database_exists(db_path):
        return False
    else:
        with sqlite3.connect(db_path) as conn:
            return True
    
def delete_database(db_name: str):
    db_path = get_db_path(db_name)
    if database_exists(db_path):
        os.remove(db_path)
        return True
    else:
        return False

def create_table(db_name: str, table_name: str, columns: str):
    if table_exists(db_name,table_name):
        return False
    else:
        db_path = get_db_path(db_name)
        with sqlite3.connect(db_path) as conn:
            conn.execute('PRAGMA journal_mode=WAL')
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            conn.commit()
            conn.execute('PRAGMA wal_checkpoint')
            return True

def delete_table(db_name: str, table_name: str):
    table_exist = table_exists(db_name,table_name)
    if table_exist:
        db_path = get_db_path(db_name)
        with sqlite3.connect(db_path) as conn:
            conn.execute('PRAGMA journal_mode=WAL')
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            conn.commit()
            conn.execute('PRAGMA wal_checkpoint')
            return True
    else:
        return False

##############################################################################
# 一般数据表的增删改查
def insert_data(db_name: str, table_name: str, columns: str, values: str):
    """
    将数据插入到指定的表中，同时更新内存数据库和磁盘数据库。
    """
    values = values.split(",")
    placeholders = ', '.join(['?' for _ in values])
    if table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        # 数据存入磁盘数据库
        with sqlite3.connect(db_path) as disk_conn:
            disk_conn.execute('PRAGMA journal_mode=WAL')
            cursor = disk_conn.cursor()
            cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
            disk_conn.commit()
            disk_conn.execute('PRAGMA wal_checkpoint')
        # 数据加入内存数据库
        memory_db = get_memory_db(db_name)
        with memory_db:
            cursor = memory_db.cursor()
            cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
            memory_db.commit()
        
        return True
    else:
        return False

def select_data(db_name: str, table_name: str, condition: str = "") -> List[Any]:
    """
    从指定的表中查询数据。
    """
    if table_exists(db_name, table_name):
        # 直接在内存数据库中查询
        memory_db = get_memory_db(db_name)
        with memory_db:
            cursor = memory_db.cursor()
            query = f"SELECT * FROM {table_name} " + (f"WHERE {condition}" if condition else "")
            cursor.execute(query)
            results = cursor.fetchall()
            return True, results
    else:
        return False, []

def delete_data(db_name: str, table_name: str, condition: str):
    """
    删除指定表中的数据，同时更新内存数据库和磁盘数据库。
    """
    if table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        # 从磁盘数据库中删除数据
        with sqlite3.connect(db_path) as disk_conn:
            disk_conn.execute('PRAGMA journal_mode=WAL')
            cursor = disk_conn.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
            disk_conn.commit()
            disk_conn.execute('PRAGMA wal_checkpoint')
        # 从内存数据库中删除数据
        memory_db = get_memory_db(db_name)
        with memory_db:
            cursor = memory_db.cursor()
            cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
            memory_db.commit()
        
        return True
    else:
        return False

def update_data(db_name: str, table_name: str, set_clause: str, condition: str):
    """
    更新指定表中的数据，同时更新内存数据库和磁盘数据库。
    """
    if table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        # 更新磁盘数据库中的数据
        with sqlite3.connect(db_path) as disk_conn:
            disk_conn.execute('PRAGMA journal_mode=WAL')
            cursor = disk_conn.cursor()
            cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {condition}")
            disk_conn.commit()
            disk_conn.execute('PRAGMA wal_checkpoint')
        # 更新内存数据库中的数据
        memory_db = get_memory_db(db_name)
        with memory_db:
            cursor = memory_db.cursor()
            cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {condition}")
            memory_db.commit()
        
        return True
    else:
        return False
    
######################################################
# 对话数据增、查
def process_data(data,db_name,user_id):
    # 获取数据表中已有多少数据条数
    rows = get_table_row_count(db_name,user_id)
    # 将对话处理成[[index,user,assistant]......]的形式
    # 自己创建索引，保证安全
    result = []
    #
    
    pass

def insert_dialogue(db_name: str, user_id: str, columns: str, values: list):
    # values:[[],[],[]]
    memory_db = get_memory_db(db_name)
    if table_exists(db_name, user_id):
        db_path = get_db_path(db_name)
        dialog = process_data(values, db_name, user_id)
        placeholders = ', '.join(['?' for _ in dialog[0]])
        
        with sqlite3.connect(db_path) as disk_conn:
            disk_conn.execute('PRAGMA journal_mode=WAL')
            cursor = disk_conn.cursor()
            # 批量插入
            cursor.executemany(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", dialog)
            disk_conn.commit()
            disk_conn.execute('PRAGMA wal_checkpoint')

        with memory_db:
            cursor = memory_db.cursor()
            cursor.executemany(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", dialog)
            memory_db.commit()

        # 将对话进行向量化并存入 faiss
        text_2_vec(user_id, dialog)
        return True
    else:
        return False

def similar_search(user_role_id: str, query: str, db_name: str) -> List[Any]:
    memory_db = get_memory_db(db_name)
    if not table_exists(db_name, user_role_id):
        return False, []
    
    # 首先进行向量化
    emb = embedding_query([query])
    # 相似度检索，距离和索引的数据格式为：[[]]
    try:
        distances, indexs = simi_search(user_role_id, emb[0])
    except:
        return False, []

    response = []
    # 进行批量查询
    with memory_db:
        cursor = memory_db.cursor()
        # 从数据库中拿出相应索引的对话，因为向量索引是从 0 开始，因此返回的索引要每个都加上 1
        values_to_search = [str(num + 1) for num in indexs[0]]
        # 构建 CASE 语句来按顺序查询
        case_statement = "CASE dialogue_id " + " ".join([f"WHEN {val} THEN {index}" for index, val in enumerate(values_to_search)]) + " END"
        search_query = f"""SELECT * FROM {user_role_id} WHERE dialogue_id IN ({','.join(['?']*len(values_to_search))}) ORDER BY {case_statement}"""
        cursor.execute(search_query, values_to_search)
        # results 格式为[(dialogue_id, user, assistant), (), ...]
        results = cursor.fetchall()
        for i in range(len(results)):
            response.append([results[i][1], results[i][2], str(distances[0][i])])

    return True, response

##########################################################################
# 提取的重要信息增、查
def insert_important_inf(db_name: str, user_id: str, columns: str, value: str):
    memory_db = get_memory_db(db_name)
    # 总结的重要信息插入
    if table_exists(db_name, user_id):
        db_path = get_db_path(db_name)
        # 获取数据表中数据的条数
        rows = get_table_row_count(db_name, user_id)
        placeholders = ', '.join(['?' for _ in [rows, value]])
        # 数据存入磁盘数据库
        with sqlite3.connect(db_path) as disk_conn:
            disk_conn.execute('PRAGMA journal_mode=WAL')
            cursor = disk_conn.cursor()
            # 单条插入
            cursor.execute(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", [rows + 1, value])
            disk_conn.commit()
            disk_conn.execute('PRAGMA wal_checkpoint')
        # 数据存入内存数据库
        with memory_db:
            cursor = memory_db.cursor()
            cursor.execute(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", [rows + 1, value])
            memory_db.commit()

        # 将对话进行向量化并存入faiss
        inf_2_vec(user_id, [value])
        return True
    else:
        return False

def similar_search_inf(user_role_id: str, query: str, db_name: str):
    memory_db = get_memory_db(db_name)
    if not table_exists(db_name, user_role_id):
        return False, []

    # 查询重要信息
    # 首先进行向量化
    emb = embedding_query([query])
    # 相似度检索,距离和索引的数据格式为：[[]]
    try:
        distances, indexs = simi_search(user_role_id, emb[0])
    except:
        return False, []

    response = []
    # 进行批量查询
    with memory_db:
        cursor = memory_db.cursor()
        # 从数据库中拿出相应索引的对话，因为向量索引是从0开始，因此返回的索引要每个都加上1
        values_to_search = [str(num + 1) for num in indexs[0]]
        # 构建 CASE 语句来按顺序查询
        case_statement = "CASE inf_id " + " ".join([f"WHEN {val} THEN {index}" for index, val in enumerate(values_to_search)]) + " END"
        search_query = f"""SELECT * FROM {user_role_id} WHERE inf_id IN ({','.join(['?']*len(values_to_search))}) ORDER BY {case_statement}"""
        cursor.execute(search_query, values_to_search)
        # results 格式为[(inf_id, inf), (), ...]
        results = cursor.fetchall()
        for i in range(len(results)):
            response.append([results[i][1], str(distances[0][i])])
    
    return True, response

###########################################################################
# 数据表内部相关操作
def get_table_row_count(db_name: str, table_name: str) -> int:
    # 数据表中的数据索引从1开始
    # 获取数据表中数据的条数
    db_path = get_db_path(db_name)
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
    return row_count

def get_table_structure(db_name: str, table_name: str) -> Dict[str, Any]:
    # 获取数据表结构
    if table_exists(db_name,table_name):
        db_path = get_db_path(db_name)
        with sqlite3.connect(db_path) as conn:
            conn.execute('PRAGMA journal_mode=WAL')
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            result = [column[1] for column in columns]
            return {"type": "str", "data": ",".join(result)}
    else:
        return False


#######################################################################
# 额外操作
# 手动触发检查点操作，确保 WAL 文件内容被合并到主数据库文件中
"""
TODO:写成定时触发
"""
def execute_checkpoint(db_name: str):
    db_path = get_db_path(db_name)
    with sqlite3.connect(db_path) as conn:
        conn.execute('PRAGMA wal_checkpoint')