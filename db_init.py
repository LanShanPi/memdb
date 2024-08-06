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
    """内存数据库连接池管理"""
    def __init__(self, size: int = 5):
        self.size = size
        self.pool: List[aiosqlite.Connection] = []
        self._lock = asyncio.Lock()

    async def initialize(self, db_path: str):
        async with self._lock:  # 使用锁来保护连接池的初始化
            for _ in range(self.size):
                try:
                    conn = await aiosqlite.connect(db_path)
                    self.pool.append(conn)
                    logging.info(f"Added new connection to pool for {db_path}.")
                except Exception as e:
                    logging.error(f"Failed to create connection: {e}")

    async def acquire(self):
        async with self._lock:  # 使用锁来管理连接的获取和释放
            while not self.pool:
                logging.warning("Waiting for available connection...")
                await asyncio.sleep(0.1)  # 等待可用连接
            logging.info("Connection acquired from pool.")
            return self.pool.pop()

    async def release(self, conn: aiosqlite.Connection):
        async with self._lock:
            self.pool.append(conn)
            logging.info("Connection released back to pool.")

    async def close_all(self):
        async with self._lock:
            for conn in self.pool:
                await conn.close()
                logging.info("Connection closed.")
            self.pool = []
            logging.info("All connections in the pool have been closed.")

# 全局内存数据库连接池字典
memory_db_pools: Dict[str, SQLitePool] = {}

async def initialize_memory_db(disk_db_path: str, db_name: str, pool_size: int = 5):
    """初始化内存数据库，将磁盘数据库中的表结构和数据复制到内存中"""
    try:
        # memory_db_path = ':memory:'
        memory_db_path = 'file::memory:?cache=shared'
        # memory_db_path = 'file::memory:?mode=memory&cache=shared'
        pool = SQLitePool(size=pool_size)
        async with aiosqlite.connect(disk_db_path) as disk_conn:
            async with aiosqlite.connect(memory_db_path) as memory_conn:
                await memory_conn.execute("PRAGMA journal_mode=WAL;")
                await copy_schema_and_data(disk_conn, memory_conn)  # 复制数据
                await pool.initialize(memory_db_path)  # 初始化连接池
                memory_db_pools[db_name] = pool
                logging.info(f"内存数据库池 {db_name} 已从 {disk_db_path} 初始化")
                await print_all_table_names(memory_conn)  # 打印内存数据库中的所有表
    except Exception as e:
        logging.error(f"无法从 {disk_db_path} 初始化内存数据库池 {db_name}: {e}")

async def print_all_table_names(memory_conn):
    """打印内存数据库中的所有表名称"""
    async with memory_conn.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
        tables = await cursor.fetchall()
        logging.info(f"内存数据库中存在的表: {[table[0] for table in tables]}")

async def copy_schema_and_data(disk_conn, memory_conn, batch_size=1000):
    """将表结构和数据从磁盘数据库复制到内存数据库"""
    try:
        await memory_conn.execute("PRAGMA foreign_keys=OFF")
        logging.info("已禁用外键约束，准备复制表结构和数据。")
        
        async with disk_conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'") as cursor:
            tables = await cursor.fetchall()
            for table in tables:
                table_name, create_sql = table
                logging.info(f"正在创建表: {table_name}，SQL: {create_sql}")

                try:
                    await memory_conn.execute(create_sql)
                    logging.info(f"表 {table_name} 创建成功。")
                    
                    async with disk_conn.execute(f"SELECT * FROM {table_name}") as table_cursor:
                        while True:
                            rows = await table_cursor.fetchmany(batch_size)
                            if not rows:
                                break
                            placeholders = ', '.join(['?' for _ in rows[0]])
                            try:
                                await memory_conn.executemany(
                                    f"INSERT INTO {table_name} VALUES ({placeholders})", rows)
                                await memory_conn.commit()
                            except Exception as insert_error:
                                logging.error(f"插入数据到表 {table_name} 时发生错误: {insert_error}")
                
                except Exception as table_error:
                    logging.error(f"创建表 {table_name} 时发生错误: {table_error}")
        
        await memory_conn.execute("PRAGMA foreign_keys=ON")
        await memory_conn.commit()
        logging.info("成功复制所有表和数据到内存数据库，外键约束已重新启用。")
    
    except Exception as e:
        logging.error(f"复制表和数据时发生总体错误: {e}")


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
    """获取内存数据库连接池"""
    pool = memory_db_pools.get(db_name)
    if pool:
        logging.info(f"找到内存数据库池 {db_name}.")
        return pool
    else:
        disk_db_path = get_db_path(db_name)
        if os.path.exists(disk_db_path):
            logging.warning(f"未找到内存数据库池 {db_name}，从磁盘初始化.")
            await initialize_memory_db(disk_db_path, db_name)  # 动态初始化
            return memory_db_pools[db_name]
        else:
            raise ValueError(f"未找到内存数据库池 {db_name}")

async def delete_memory_db(db_name: str):
    """删除内存数据库"""
    if db_name in memory_db_pools:
        pool = memory_db_pools.pop(db_name)
        await pool.close_all()
        logging.info(f"内存数据库池 {db_name} 已被移除并关闭.")
    else:
        logging.warning(f"未找到内存数据库池 {db_name} 以删除.")

