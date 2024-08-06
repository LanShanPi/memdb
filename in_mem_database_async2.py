import aiosqlite
import aiofiles
from typing import List, Any, Dict
import os
from config import *
import logging
from embd_domain.emb_text_v2 import EmbeddingService
from faiss_domain.faiss_process import *
import aiosqlite
from typing import List, Any, Dict
from db_init2 import get_memory_db_pool,initialize_memory_db,delete_memory_db,execute_query

logging.basicConfig(
    level=logging.INFO,  # 确保日志级别设置为INFO
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler()]  # 设定输出到控制台
)
emb_model = EmbeddingService()

# 检查数据库是否存在
async def database_exists(db_name: str) -> bool:
    db_path = get_db_path(db_name)
    return os.path.exists(db_path)

# 创建数据库
async def create_database(db_name: str):
    db_path = get_db_path(db_name)
    if await database_exists(db_name):
        return False
    else:
        async with aiosqlite.connect(db_path) as conn:
            pass
        # 动态初始化内存数据库池
        await initialize_memory_db(db_path, db_name)
        logging.info(f"数据库 {db_name} 已添加至内存")
        return True

async def delete_database(db_name: str):
    db_path = get_db_path(db_name)
    if await database_exists(db_name):
        # 先删除内存数据库
        await delete_memory_db(db_name)
        logging.info(f"数据库 {db_name} 已从内存删除.")
        # 删除磁盘数据库
        os.remove(db_path)
        logging.info(f"数据库 {db_name} 已从磁盘删除.")
        return True
    else:
        logging.warning(f"数据库 {db_name} 不存在.")
        return False

# 创建数据表
async def create_table(db_name: str, table_name: str, columns: str):
    try:
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not table_exists:
            logging.error(f"表 {table_name} 在数据库 {db_name} 中不存在")
            return False
        
        db_path = get_db_path(db_name)
        # 在磁盘数据库中创建表
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            async with conn.cursor() as cursor:
                await cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            await conn.commit()
            await conn.execute('PRAGMA wal_checkpoint')
            logging.info(f"数据表 {table_name} 已在磁盘数据库 {db_name} 中创建完成.")
        # 在内存数据库中创建表
        await execute_query(db_name,f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
        return True
    except Exception as e:
        logging.error(f"添加数据表时发生错误: {e}")
        return False, []
# 删除数据表
async def delete_table(db_name: str, table_name: str):
    try:
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not table_exists:
            logging.error(f"表 {table_name} 在数据库 {db_name} 中不存在")
            return False
        
        db_path = get_db_path(db_name)
        # 从磁盘数据库中删除表
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            async with conn.cursor() as cursor:
                await cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            await conn.commit()
            await conn.execute('PRAGMA wal_checkpoint')
        # 从内存数据库中删除表
        await execute_query(db_name,f"DROP TABLE IF EXISTS {table_name}")
        return True
    except Exception as e:
        logging.error(f"添加数据表时发生错误: {e}")
        return False, []


# 插入数据到指定表中
async def insert_data(db_name: str, table_name: str, columns: str, values: str):
    values = values.split(",")
    placeholders = ', '.join(['?' for _ in values])
    
    try:
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not table_exists:
            logging.error(f"表 {table_name} 在数据库 {db_name} 中不存在")
            return False
        db_path = get_db_path(db_name)
        # 插入数据到磁盘数据库
        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            async with disk_conn.cursor() as cursor:
                await cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')
        # 插入数据到内存数据库
        await execute_query(db_name,f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
        return True
    except Exception as e:
        logging.error(f"添加数据时发生错误: {e}")
        return False, []



# 查询指定表中的数据
async def select_data(db_name: str, table_name: str, condition: str = "") -> List[Any]:
    try:
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not table_exists:
            logging.error(f"表 {table_name} 在数据库 {db_name} 中不存在")
            return False
        query = f"SELECT * FROM {table_name} " + (f"WHERE {condition}" if condition else "")
        results = await execute_query(db_name, query)
        return True, results
    except Exception as e:
        logging.error(f"搜索数据时发生错误: {e}")
        return False, []


# 删除指定表中的数据
async def delete_data(db_name: str, table_name: str, condition: str):
    try:
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not table_exists:
            logging.error(f"表 {table_name} 在数据库 {db_name} 中不存在")
            return False
        
        db_path = get_db_path(db_name)
        # 从磁盘数据库中删除数据
        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            async with disk_conn.cursor() as cursor:
                await cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')

        # 从内存数据库中删除数据
        await execute_query(db_name,f"DELETE FROM {table_name} WHERE {condition}")
        return True
    except Exception as e:
        logging.error(f"删除数据时发生错误: {e}")
        return False


# 更新指定表中的数据
async def update_data(db_name: str, table_name: str, set_clause: str, condition: str):
    try:
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not table_exists:
            logging.error(f"表 {table_name} 在数据库 {db_name} 中不存在")
            return False
        db_path = get_db_path(db_name)
        # 更新磁盘数据库中的数据
        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            async with disk_conn.cursor() as cursor:
                await cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {condition}")
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')
        # 更新内存数据库中的数据
        await execute_query(db_name,f"UPDATE {table_name} SET {set_clause} WHERE {condition}")
        return True
    except Exception as e:
        logging.error(f"更新数据时发生错误: {e}")
        return False
    
# 处理对话数据
async def process_data(data, db_name, user_id):
    # 获取数据表中已有多少数据条数
    rows = await get_table_row_count(db_name, user_id)
    # 将对话处理成[[index, user, assistant]......]的形式
    # 自己创建索引，保证安全
    result = []
    #
    pass

# 插入对话数据
async def insert_dialogue(db_name: str, user_id: str, columns: str, values: list):
    try:
        # 检查表是否存在
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (user_id,))
        if not table_exists:
            logging.error(f"表 {user_id} 在数据库 {db_name} 中不存在")
            return False

        dialog = await process_data(values, db_name, user_id)
        placeholders = ', '.join(['?' for _ in dialog[0]])

        # 插入到内存数据库
        await execute_query(db_name, f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", dialog, many=True)
        
        # 插入到磁盘数据库
        db_path = get_db_path(db_name)
        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            await disk_conn.executemany(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", dialog)
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')

        logging.info(f"向数据库中添加对话数据操作完成")

        # 将对话进行向量化并存入 faiss
        await emb_model.text_2_vec(user_id, dialog)
        return True
    except Exception as e:
        logging.error(f"插入对话数据时发生错误: {e}")
        return False

# 相似度搜索对话数据
async def similar_search(user_role_id: str, query: str, db_name: str) -> List[Any]:
    try:
        # 检查表是否存在
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (user_role_id,))
        if not table_exists:
            logging.error(f"表 {user_role_id} 在数据库 {db_name} 中不存在")
            return False, []

        # 进行向量化
        emb = await emb_model.embedding_query([query])
        # 相似度检索
        distances, indexs = simi_search(user_role_id, emb[0])

        # 进行批量查询
        values_to_search = [str(num + 1) for num in indexs[0]]
        # 构建 CASE 语句来按顺序查询
        case_statement = "CASE dialogue_id " + " ".join([f"WHEN {val} THEN {index}" for index, val in enumerate(values_to_search)]) + " END"
        search_query = f"""SELECT * FROM {user_role_id} WHERE dialogue_id IN ({','.join(['?']*len(values_to_search))}) ORDER BY {case_statement}"""
        
        results = await execute_query(db_name, search_query, values_to_search)

        response = [[result[1], result[2], str(distances[0][i])] for i, result in enumerate(results)]

        logging.info(f"在数据库中搜索相似数据操作完成")
        return True, response
    except Exception as e:
        logging.error(f"搜索相似数据时发生错误: {e}")
        return False, []

# 向内存数据库中插入重要信息
async def insert_important_inf(db_name: str, user_id: str, columns: str, value: str):
    try:
        # 检查内存中表是否存在
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (user_id,))
        if not table_exists:
            logging.error(f"内存数据库 {db_name} 中不存在表 {user_id}。")
            return False

        # 获取数据表中数据的条数
        rows = await execute_query(db_name, f"SELECT COUNT(*) FROM {user_id}")
        rows = rows[0][0] if rows else 0

        placeholders = ', '.join(['?' for _ in [rows + 1, value]])

        # 数据存入内存数据库
        await execute_query(db_name, f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", (rows + 1, value))
        
        logging.info(f"向内存数据表 {user_id} 中添加重要信息数据成功。")

        # 数据存入磁盘数据库
        db_path = get_db_path(db_name)
        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            await disk_conn.execute(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", (rows + 1, value))
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')

        # 将对话进行向量化并存入 faiss
        await emb_model.inf_2_vec(user_id, [value])
        return True
    except Exception as e:
        logging.error(f"插入数据时发生错误: {e}")
        return False

async def similar_search_inf(user_role_id: str, query: str, db_name: str):
    try:
        # 检查表是否存在
        table_exists = await execute_query(db_name, f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (user_role_id,))
        if not table_exists:
            return False, []

        # 首先进行向量化
        emb = await emb_model.embedding_query(data=[query])
        # 相似度检索，距离和索引的数据格式为：[[]]
        distances, indexs = simi_search(user_role_id, emb[0])

        response = []
        # 进行批量查询
        values_to_search = [str(num + 1) for num in indexs[0]]
        # 构建 CASE 语句来按顺序查询
        case_statement = "CASE inf_id " + " ".join([f"WHEN {val} THEN {index}" for index, val in enumerate(values_to_search)]) + " END"
        search_query = f"""SELECT * FROM {user_role_id} WHERE inf_id IN ({','.join(['?']*len(values_to_search))}) ORDER BY {case_statement}"""
        
        results = await execute_query(db_name, search_query, values_to_search)
        
        for i, result in enumerate(results):
            response.append([result[1], str(distances[0][i])])

        logging.info(f"在内存数据表中搜索重要信息数据操作完成")
        return True, response
    except Exception as e:
        logging.error(f"搜索数据时发生错误: {e}")
        return False, []



# 获取数据表中的数据条数
async def get_table_row_count(db_name: str, table_name: str) -> int:
    # 数据表中的数据索引从1开始
    # 获取数据表中数据的条数
    db_path = get_db_path(db_name)
    async with aiosqlite.connect(db_path) as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = (await cursor.fetchone())[0]
    return row_count

# 获取数据表结构
async def get_table_structure(db_name: str, table_name: str) -> Dict[str, Any]:
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        pool = await get_memory_db_pool(db_name)
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            async with conn.cursor() as cursor:
                await cursor.execute(f"PRAGMA table_info({table_name});")
                columns = await cursor.fetchall()
                result = [column[1] for column in columns]
                return {"type": "str", "data": ",".join(result)}
    else:
        return False