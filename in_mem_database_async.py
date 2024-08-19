import aiosqlite
import aiofiles
from typing import List, Any, Dict
import os
from config import *
import logging
from embd_domain.emb_text_v2 import EmbeddingService
from spacy_domain.spacy_server import spacy_process
from faiss_domain.faiss_process import *
import aiosqlite
from typing import List, Any, Dict
from db_init import get_memory_db_pool,initialize_memory_db,delete_memory_db,memory_db_pools
<<<<<<< HEAD
from functional_function import get_time,replace_dates_in_sentence
from llm_domain import openai_llm
from prompt_domain.llm_propmt import Judge_System
=======
from functional_function import get_time,get_time_scope,replace_dates_in_sentence
>>>>>>> 4354fe1a006e05a8294cd9db047fc0224262cf96

logging.basicConfig(
    level=logging.INFO,  # 确保日志级别设置为INFO
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler()]  # 设定输出到控制台
)
emb_model = EmbeddingService()
spacy_processer = spacy_process()

# 检查数据库是否存在
async def database_exists(db_name: str) -> bool:
    db_path = get_db_path(db_name)
    return os.path.exists(db_path)

# 检查数据表是否存在
async def table_exists(db_name: str, table_name: str) -> bool:
    db_path = get_db_path(db_name)
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute('PRAGMA journal_mode=WAL')
        cursor = await conn.cursor()
        await cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return await cursor.fetchone() is not None


async def memory_table_exists(pool, table_name: str) -> bool:
    memory_db = await pool.acquire()
    try:
        async with memory_db.cursor() as cursor:
            await cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            result = await cursor.fetchone()
            logging.info(f"查询数据表 {table_name} 是否在内存数据库中")
            return result is not None
    except Exception as e:
        logging.error(f"查询内存数据库时发生错误: {e}")
        return False
    finally:
        logging.info(f"查询数据表 {table_name} 是否在内存数据库中操作完成，释放内存数据库连接回连接池。")
        await pool.release(memory_db)


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
    if await table_exists(db_name, table_name):
        logging.warning(f"数据表 {table_name} 已经存在于数据库 {db_name}.")
        return False
    else:
        db_path = get_db_path(db_name)
        pool = await get_memory_db_pool(db_name)
        # 在磁盘数据库中创建表
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            async with conn.cursor() as cursor:
                await cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            await conn.commit()
            await conn.execute('PRAGMA wal_checkpoint')
            logging.info(f"数据表 {table_name} 已在磁盘数据库 {db_name} 中创建完成.")
        # 在内存数据库中创建表
        memory_db = await pool.acquire()
        try:
            async with memory_db.cursor() as cursor:
                await cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            await memory_db.commit()
            logging.info(f"数据表 {table_name} 已在内存数据库 {db_name} 中创建完成.")
        finally:
            await pool.release(memory_db)
            logging.info("在内存数据库中创建数据表完成，释放内存数据库链接进链接池")
        return True

# 删除数据表
async def delete_table(db_name: str, table_name: str):
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        pool = await get_memory_db_pool(db_name)

        # 从磁盘数据库中删除表
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            async with conn.cursor() as cursor:
                await cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            await conn.commit()
            await conn.execute('PRAGMA wal_checkpoint')
        # 从内存数据库中删除表
        memory_db = await pool.acquire()
        try:
            async with memory_db.cursor() as cursor:
                await cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            await memory_db.commit()
            logging.info(f"数据表 {table_name} 已从内存数据库 {db_name} 中删除")
        finally:
            await pool.release(memory_db)
            logging.info(f"删除内存数据库操作完成，释放内存数据库链接进链接池")
        return True
    else:
        logging.warning(f"数据表 {table_name} 不存在于数据库 {db_name} 中")
        return False


# 插入数据到指定表中
async def insert_data(db_name: str, table_name: str, columns: str, values: str):
    # 获取时间戳
    _time = get_time()
    values = values.split(",")
    values.append(_time)
    placeholders = ', '.join(['?' for _ in values])

    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        pool = await get_memory_db_pool(db_name)

        # 插入数据到磁盘数据库
        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            async with disk_conn.cursor() as cursor:
                await cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')

        # 插入数据到内存数据库
        memory_db = await pool.acquire()  # 直接获取连接
        try:
            async with memory_db.cursor() as cursor:
                await cursor.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", values)
            await memory_db.commit()
            logging.info(f"新数据已添加进内存数据库 {db_name} 的数据表 {table_name} 中")
        finally:
            await pool.release(memory_db)  # 确保连接被释放
            logging.info(f"向内存数据库中的数据表添加数据操作完成，释放内存数据库链接进链接池")
        return True
    else:
        logging.warning(f"数据表 {table_name} 不存在于数据库 {db_name} 中")
        return False

async def ensure_memory_db_initialized(db_name: str):
    """确保内存数据库池已初始化"""
    pool = memory_db_pools.get(db_name)
    if not pool:
        disk_db_path = get_db_path(db_name)
        if os.path.exists(disk_db_path):
            logging.info(f"Initializing memory database for {db_name} from disk.")
            await initialize_memory_db(disk_db_path, db_name)
        else:
            raise ValueError(f"Database {db_name} does not exist on disk.")


# 查询指定表中的数据
async def select_data(db_name: str, table_name: str, condition: str = "") -> List[Any]:
    if await table_exists(db_name, table_name):
        await ensure_memory_db_initialized(db_name)  # 确保数据库池已初始化
        pool = await get_memory_db_pool(db_name)
        
        if not await memory_table_exists(pool, table_name):
            logging.warning(f"数据表 {table_name} 不存在于内存数据库 {db_name} 中")
            return False, []

        memory_db = await pool.acquire()
        try:
            async with memory_db.cursor() as cursor:
                query = f"SELECT * FROM {table_name} " + (f"WHERE {condition}" if condition else "")
                await cursor.execute(query)
                results = await cursor.fetchall()
                return True, results
        finally:
            await pool.release(memory_db)
            logging.info(f"在内存数据库中进行数据查询操作完成，释放内存数据库链接进链接池")

    else:
        logging.warning(f"数据表 {table_name} 不存在于数据库 {db_name} 中")
        return False, []


# 删除指定表中的数据
async def delete_data(db_name: str, table_name: str, condition: str):
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        pool = await get_memory_db_pool(db_name)

        # 从磁盘数据库中删除数据
        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            async with disk_conn.cursor() as cursor:
                await cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')

        # 从内存数据库中删除数据
        memory_db = await pool.acquire()
        try:
            async with memory_db.cursor() as cursor:
                await cursor.execute(f"DELETE FROM {table_name} WHERE {condition}")
            await memory_db.commit()
            logging.info(f"指定数据已从内存数据库 {db_name} 的数据表 {table_name} 中删除")
        finally:
            await pool.release(memory_db)
            logging.info(f"从删除内存数据表中的数据完成，释放内存数据库链接进链接池")

        return True
    else:
        logging.warning(f"数据表 {table_name} 不存在于数据库 {db_name} 中")
        return False


# 更新指定表中的数据
async def update_data(db_name: str, table_name: str, set_clause: str, condition: str):
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        pool = await get_memory_db_pool(db_name)
        # 更新磁盘数据库中的数据
        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            async with disk_conn.cursor() as cursor:
                await cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {condition}")
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')
        # 更新内存数据库中的数据
        memory_db = await pool.acquire()
        try:
            async with memory_db.cursor() as cursor:
                await cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {condition}")
            await memory_db.commit()
            logging.info(f"指定数据已在内存数据库 {db_name} 的数据表 {table_name} 中进行更新")
        finally:
            await pool.release(memory_db)
            logging.info(f"更新内存数据表中的数据操作完成，释放内存数据库链接进链接池")
        return True
    else:
        return False

# 处理对话数据
async def process_data(data, db_name, user_id):
    # 获取数据表中已有多少数据条数
    rows = await get_table_row_count(db_name, user_id)
    _time = get_time()
    # 将对话处理成[[index, user, assistant,time]......]的形式,加上时间戳
    # 自己创建索引，保证安全
    result = []
    #
    pass

# 插入对话数据
async def insert_dialogue(db_name: str, user_id: str, columns: str, values: list):
    # values:[[],[],[]]
    pool = await get_memory_db_pool(db_name)
    if await table_exists(db_name, user_id):
        db_path = get_db_path(db_name)
        dialog = await process_data(values, db_name, user_id)
        placeholders = ', '.join(['?' for _ in dialog[0]])

        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            async with disk_conn.cursor() as cursor:
                # 批量插入
                await cursor.executemany(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", dialog)
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')
        
        memory_db = await pool.acquire()
        try:
            async with memory_db.cursor() as cursor:
                await cursor.executemany(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", dialog)
            await memory_db.commit()
        finally:
            await pool.release(memory_db)
            logging.info(f"向内存数据库中添加对话数据操作完成，释放内存数据库链接进链接池")

        # 将对话进行向量化并存入 faiss
        await emb_model.text_2_vec(user_id, dialog)
        return True
    else:
        return False

# 相似度搜索对话数据
async def similar_search(user_role_id: str, query: str, db_name: str) -> List[Any]:
    pool = await get_memory_db_pool(db_name)
    if not await table_exists(db_name, user_role_id):
        return False, []
    
    # 首先进行向量化
    emb = await emb_model.embedding_query([query])
    # 相似度检索，距离和索引的数据格式为：[[]]
    try:
        distances, indexs = simi_search(user_role_id, emb[0])
    except:
        return False, []

    response = []
    memory_db = await pool.acquire()
    # 进行批量查询
    try:
        async with memory_db.cursor() as cursor:
            # 从数据库中拿出相应索引的对话，因为向量索引是从0开始，因此返回的索引要每个都加上1
            values_to_search = [str(num + 1) for num in indexs[0]]
            # 构建 CASE 语句来按顺序查询
            case_statement = "CASE dialogue_id " + " ".join([f"WHEN {val} THEN {index}" for index, val in enumerate(values_to_search)]) + " END"
            search_query = f"""SELECT * FROM {user_role_id} WHERE dialogue_id IN ({','.join(['?']*len(values_to_search))}) ORDER BY {case_statement}"""
            await cursor.execute(search_query, values_to_search)
            # results 格式为[(dialogue_id, user, assistant), (), ...]
            results = await cursor.fetchall()
            for i in range(len(results)):
                response.append([results[i][1], results[i][2], str(distances[0][i])])
    finally:
            await pool.release(memory_db)
            logging.info(f"在内存数据中搜索相似数据操作完成，释放内存数据库链接进链接池")

    return True, response

# 向内存数据库中插入重要信息
async def insert_important_inf(db_name: str, user_id: str, columns: str, value: str):
    """
    # 判断信息重要性，以此来判断是否需要进行存储
    inf_important_or_not = openai_llm(value,Judge_System)
    if "无重要信息" in inf_important_or_not:
        return False,"对话无重要信息不进行存储"
    """
    
    pool = await get_memory_db_pool(db_name)
    # 检查内存中表是否存在
    if not await memory_table_exists(pool, user_id):
        logging.error(f"内存数据库 {db_name} 中不存在表 {user_id}。")
        return False

    # 总结的重要信息插入
    if await table_exists(db_name, user_id):
        db_path = get_db_path(db_name)
        # 获取数据表中数据的条数
        rows = await get_table_row_count(db_name, user_id)
        # 获取时间
        _time = get_time()
        # 修正句子中关于时间的词
        value = replace_dates_in_sentence(value)
        placeholders = ', '.join(['?' for _ in [rows, value, _time]])

        # 数据存入磁盘数据库
        async with aiosqlite.connect(db_path) as disk_conn:
            await disk_conn.execute('PRAGMA journal_mode=WAL')
            async with disk_conn.cursor() as cursor:
                # 单条插入
                await cursor.execute(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", [rows + 1, value, _time])
            await disk_conn.commit()
            await disk_conn.execute('PRAGMA wal_checkpoint')

        # 数据存入内存数据库
        memory_db = await pool.acquire()
        try:
            async with memory_db.cursor() as cursor:
                await cursor.execute(f"INSERT INTO {user_id} ({columns}) VALUES ({placeholders})", [rows + 1, value, _time])
            await memory_db.commit()
            logging.info(f"向内存数据表 {user_id} 中添加重要信息数据成功。")
        finally:
            await pool.release(memory_db)
            logging.info("释放内存数据库连接，将连接返回连接池。")
        # 将对话进行向量化并存入 faiss
        await emb_model.inf_2_vec(user_id, [value])
        return True
    else:
        logging.error(f"磁盘数据库 {db_name} 中不存在表 {user_id}。")
        return False
    
# 相似度搜索重要信息
async def similar_search_inf(user_role_id: str, query: str, db_name: str):
    response = []
    pool = await get_memory_db_pool(db_name)
    if not await table_exists(db_name, user_role_id):
        return False, response
    
    # 查询重要信息
    # 首先进行向量化
    # 修正关于时间的词
    query = replace_dates_in_sentence(query)
    emb = await emb_model.embedding_query(data=[query])

    """
    # 暂时废弃
    # 获取query中的时间词，用以确定数据索引时间范围
    # time_words = spacy_processer.get_time_text(query)
    time_words = []
    if time_words:
        # time_scope 格式为[[start_time,end_time],[]]
        time_scope = get_time_scope(time_words)
        if time_scope:
            memory_db = await pool.acquire()
            try:
                async with memory_db.cursor() as cursor:
                    # 创建查询语句，选择在日期范围内的所有记录
                    search_query = f"SELECT * FROM {user_role_id}WHERE time BETWEEN ? AND ?ORDER BY timestamp"
                    # 执行查询，传递开始和结束日期作为参数
                    await cursor.execute(search_query, (time_scope[0][0], time_scope[0][1]))
                    # 获取结果，格式为 [(inf_id, inf, ...), (...), ...]
                    results = await cursor.fetchall()
                    infs = []
                    for i in range(len(results)):
                        infs.append(results[i][1])
                    infs_vec = await emb_model.embedding_query(data=infs)
                    distances, indexs = scope_search(emb[0],infs_vec)
                    for index, value in enumerate(index[0]):
                        response.append([infs[value], str(distances[0][index])])
            finally:
                await pool.release(memory_db)
                logging.info("在内存数据表中搜索指定时间段内的数据操作完成，释放内存数据库链接进链接池")
            # return先放在这
            return True, response
    """

    # 若没有时间相关的词，就进行全数据表索引
    # 相似度检索，距离和索引的数据格式为：[[]]
    try:
        distances, indexs = simi_search(user_role_id, emb[0])
        logging.info(f"搜索到的数据索引为{indexs}")
    except:
        return False, []

    # 进行全数据表批量查询
    memory_db = await pool.acquire()
    try:
        async with memory_db.cursor() as cursor:
            # 从数据库中拿出相应索引的对话，因为向量索引是从0开始，因此返回的索引要每个都加上1
            values_to_search = [str(num + 1) for num in indexs[0]]
            # 构建 CASE 语句来按顺序查询
            case_statement = "CASE inf_id " + " ".join([f"WHEN {val} THEN {index}" for index, val in enumerate(values_to_search)]) + " END"
            search_query = f"""SELECT * FROM {user_role_id} WHERE inf_id IN ({','.join(['?']*len(values_to_search))}) ORDER BY {case_statement}"""
            await cursor.execute(search_query, values_to_search)
            # results 格式为[(inf_id, inf), (), ...]
            results = await cursor.fetchall()
            for i in range(len(results)):
                response.append([results[i][1], str(distances[0][i])])

    finally:
            await pool.release(memory_db)
            logging.info(f"在内存数据表中搜索重要信息数据操作完成，释放内存数据库链接进链接池")
    return True, response

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