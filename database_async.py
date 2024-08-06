import aiosqlite
from typing import List, Any, Dict
import os
from config import *
import logging

async def database_exists(db_name: str) -> bool:
    db_path = get_db_path(db_name)
    return os.path.exists(db_path)

async def table_exists(db_name: str, table_name: str) -> bool:
    db_path = get_db_path(db_name)
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute('PRAGMA journal_mode=WAL')
        cursor = await conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        return await cursor.fetchone() is not None

async def create_database(db_name: str):
    db_path = get_db_path(db_name)
    if await database_exists(db_path):
        return False
    else:
        async with aiosqlite.connect(db_path) as conn:
            return True

async def delete_database(db_name: str):
    db_path = get_db_path(db_name)
    if await database_exists(db_path):
        os.remove(db_path)
        return True
    else:
        return False

async def create_table(db_name: str, table_name: str, columns: str):
    if await table_exists(db_name, table_name):
        return False
    else:
        db_path = get_db_path(db_name)
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            await conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")
            await conn.commit()
            await conn.execute('PRAGMA wal_checkpoint')
            return True

async def delete_table(db_name: str, table_name: str):
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            await conn.execute(f"DROP TABLE {table_name}")
            await conn.commit()
            await conn.execute('PRAGMA wal_checkpoint')
            return True
    else:
        return False

async def insert_data(db_name: str, table_name: str, data: Dict[str, Any]):
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            columns = ', '.join(data.keys())
            placeholders = ', '.join('?' for _ in data.values())
            await conn.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})", tuple(data.values()))
            await conn.commit()
            await conn.execute('PRAGMA wal_checkpoint')
            return True
    else:
        return False

async def update_data(db_name: str, table_name: str, updates: Dict[str, Any], condition: str):
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            set_clause = ', '.join(f"{col} = ?" for col in updates.keys())
            await conn.execute(f"UPDATE {table_name} SET {set_clause} WHERE {condition}", tuple(updates.values()))
            await conn.commit()
            await conn.execute('PRAGMA wal_checkpoint')
            return True
    else:
        return False

async def delete_data(db_name: str, table_name: str, condition: str):
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            await conn.execute(f"DELETE FROM {table_name} WHERE {condition}")
            await conn.commit()
            await conn.execute('PRAGMA wal_checkpoint')
            return True
    else:
        return False

async def select_data(db_name: str, table_name: str, condition: str = "") -> List[Any]:
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            query = f"SELECT * FROM {table_name} " + (f"WHERE {condition}" if condition else "")
            cursor = await conn.execute(query)
            results = await cursor.fetchall()
            return True, results
    else:
        return False, []

async def get_table_structure(db_name: str, table_name: str) -> Dict[str, Any]:
    if await table_exists(db_name, table_name):
        db_path = get_db_path(db_name)
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute('PRAGMA journal_mode=WAL')
            cursor = await conn.execute(f"PRAGMA table_info({table_name});")
            columns = await cursor.fetchall()
            result = [column[1] for column in columns]
            return {"type": "str", "data": ",".join(result)}
    else:
        return False

async def execute_checkpoint(db_name: str):
    db_path = get_db_path(db_name)
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute('PRAGMA wal_checkpoint')
