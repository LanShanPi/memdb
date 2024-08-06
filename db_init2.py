import aiosqlite
import asyncio
import logging
import os
from typing import Dict, List
from config import get_db_path  # 假设这个函数已经定义，用于获取数据库路径

logging.basicConfig(
    level=logging.INFO,  # 确保日志级别设置为INFO
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler()]  # 设定输出到控制台
)

class SQLitePool:
    def __init__(self, size: int = 5):
        self.size = size
        self.pool: List[aiosqlite.Connection] = []
        self._lock = asyncio.Lock()
        self.db_path = None

    async def initialize(self, db_path: str):
        self.db_path = db_path
        async with self._lock:
            conn = await aiosqlite.connect(db_path, uri=True)
            await conn.execute("PRAGMA journal_mode=WAL;")
            self.pool = [conn] * self.size
            logging.info(f"Initialized pool with {self.size} connections to {db_path}.")

    async def acquire(self):
        async with self._lock:
            while not self.pool:
                logging.warning("Waiting for available connection...")
                await asyncio.sleep(0.1)
            return self.pool.pop()

    async def release(self, conn: aiosqlite.Connection):
        async with self._lock:
            if len(self.pool) < self.size:
                self.pool.append(conn)
                logging.info("Connection released back to pool.")
            else:
                await conn.close()
                logging.info("Excess connection closed.")

    async def close_all(self):
        async with self._lock:
            for conn in self.pool:
                await conn.close()
            self.pool = []
            logging.info("All connections in the pool have been closed.")

# 全局内存数据库连接池字典
memory_db_pools: Dict[str, SQLitePool] = {}

async def initialize_memory_db(disk_db_path: str, db_name: str, pool_size: int = 5):
    try:
        memory_db_path = f':memory:'
        pool = SQLitePool(size=pool_size)
        await pool.initialize(memory_db_path)
        
        async with aiosqlite.connect(disk_db_path) as disk_conn:
            memory_conn = await pool.acquire()
            try:
                await copy_schema_and_data(disk_conn, memory_conn)
                memory_db_pools[db_name] = pool
                logging.info(f"内存数据库池 {db_name} 已从 {disk_db_path} 初始化")
                await print_all_table_names(memory_conn)
            finally:
                await pool.release(memory_conn)
    except Exception as e:
        logging.error(f"无法从 {disk_db_path} 初始化内存数据库池 {db_name}: {e}")

async def print_all_table_names(memory_conn):
    """打印内存数据库中的所有表名称"""
    async with memory_conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
        tables = await cursor.fetchall()
        logging.info(f"内存数据库中存在的表: {[table[0] for table in tables]}")

async def copy_schema_and_data(disk_conn, memory_conn, batch_size=1000):
    try:
        await memory_conn.execute("PRAGMA foreign_keys=OFF")
        await memory_conn.execute("BEGIN TRANSACTION")
        
        async with disk_conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'") as cursor:
            tables = await cursor.fetchall()
            for table_name, create_sql in tables:
                await memory_conn.execute(create_sql)
                async with disk_conn.execute(f"SELECT * FROM {table_name}") as table_cursor:
                    while True:
                        rows = await table_cursor.fetchmany(batch_size)
                        if not rows:
                            break
                        placeholders = ', '.join(['?' for _ in rows[0]])
                        await memory_conn.executemany(
                            f"INSERT INTO {table_name} VALUES ({placeholders})", rows)
        
        await memory_conn.execute("PRAGMA foreign_keys=ON")
        await memory_conn.execute("COMMIT")
        logging.info("成功复制所有表和数据到内存数据库")
    
    except Exception as e:
        await memory_conn.execute("ROLLBACK")
        logging.error(f"复制表和数据时发生错误: {e}")
        raise

async def initialize_all_memory_dbs(db_paths: Dict[str, str], pool_size: int = 5):
    """初始化所有内存数据库"""
    tasks = [initialize_memory_db(db_path, db_name, pool_size) for db_name, db_path in db_paths.items()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result, db_name in zip(results, db_paths.keys()):
        if isinstance(result, Exception):
            logging.error(f"数据库 {db_name} 初始化失败: {result}")
        else:
            logging.info(f"数据库 {db_name} 初始化成功")
    logging.info("数据库初始化函数已启动，所有内存数据库初始化完成.")

async def get_memory_db_pool(db_name: str) -> SQLitePool:
    pool = memory_db_pools.get(db_name)
    if pool:
        logging.info(f"找到内存数据库池 {db_name}.")
        return pool
    else:
        disk_db_path = get_db_path(db_name)
        if os.path.exists(disk_db_path):
            logging.warning(f"未找到内存数据库池 {db_name}，从磁盘初始化.")
            await initialize_memory_db(disk_db_path, db_name)
            return memory_db_pools[db_name]
        else:
            raise ValueError(f"未找到磁盘数据库 {db_name}")

async def execute_query(db_name: str, query: str, parameters: tuple = None):
    pool = await get_memory_db_pool(db_name)
    conn = await pool.acquire()
    try:
        async with conn.execute(query, parameters) as cursor:
            result = await cursor.fetchall()
        return result
    finally:
        await pool.release(conn)

async def delete_memory_db(db_name: str):
    """删除内存数据库"""
    if db_name in memory_db_pools:
        pool = memory_db_pools.pop(db_name)
        await pool.close_all()
        logging.info(f"内存数据库池 {db_name} 已被移除并关闭.")
    else:
        logging.warning(f"未找到内存数据库池 {db_name} 以删除.")

