

import sqlite3
from config import get_db_path
import os
import datetime,pytz

conn = sqlite3.connect("/home/kuaipan/memdb/db_domain/dialogue.db")
cursor = conn.cursor()

# cursor.execute(f"CREATE TABLE IF NOT EXISTS test_table (id TEXT PRIMARY KEY, year)")
# conn.commit()

# values = "1,1998".split(",")
# placeholders = ', '.join(['?' for _ in values])
# cursor.execute(f"INSERT INTO test_table (id,year) VALUES ({placeholders})", values)
# conn.commit()

# # 给已有表添加时间字段
# cursor.execute('''
# ALTER TABLE user1_role1 ADD COLUMN time TIMESTAMP
# ''')


# 为现有数据填充一个默认时间戳（例如，填充为一年前的日期）
default_date = '2024-08-05 00:00:00'
cursor.execute('''UPDATE user1_role1 SET time = ?WHERE time IS NULL''', (default_date,))

# # 自动添加时间戳
# local_tz = pytz.timezone('Asia/Shanghai')
# local_time = datetime.datetime.now().now(local_tz)
# cursor.execute('''INSERT INTO test_table (id, year, created_at)
# VALUES (?, ?, ?)
# ''', ('3', '1990',local_time.strftime('%Y-%m-%d %H:%M:%S')))

# # 更新数据并自动设置更新时间戳
# cursor.execute('''
# UPDATE test_table
# SET year = ?, updated_at = CURRENT_TIMESTAMP
# WHERE id = ?
# ''', ('1934', 1)) 


# 提交更改
conn.commit()
# # 关闭连接
conn.close()






# # def execute_checkpoint(db_name: str):
# #     db_path = get_db_path(db_name)
# #     with sqlite3.connect(db_path) as conn:
# #         conn.execute('PRAGMA wal_checkpoint')
# # execute_checkpoint("paipan_data_book")

