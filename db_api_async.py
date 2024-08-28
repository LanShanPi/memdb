
from fastapi import FastAPI, HTTPException
from db_schema import *
from contextlib import asynccontextmanager
from typing import List, Any
import os
import in_mem_database_async as db
import uvicorn
from db_init import initialize_all_memory_dbs
import logging
import config

app = FastAPI()

################################################################
# 初始化所有数据库
@app.on_event("startup")
async def startup_event():
    await initialize_all_memory_dbs(config.get_db_inf())
    logging.info("服务启动，所有内存数据库初始化完成.")

# @app.on_event("shutdown")
# async def shutdown_event():
#     for pool in memory_db_pools.values():
#         await pool.close_all()
#     logging.info("All memory database pools have been closed.")

#################################################################
# 数据库数据表创、删、查
@app.post("/create_database/{db_name}")
async def create_database(db_name: str):
    logging.info("----------create database----------")
    logging.info(f"database id <{db_name}>")
    mark = await db.create_database(db_name)
    if mark:
        return {"message": f"Database {db_name} created successfully."}
    else:
        return {"message": f"Database {db_name} already exists."}

@app.delete("/delete_database/{db_name}")
async def delete_database(db_name: str):
    mark = await db.delete_database(db_name)
    if mark:
        return {"message": f"Database {db_name} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Database not found")

@app.post("/create_table/")
async def create_table(schema: TableSchema):
    # schema.columns: id INTEGER PRIMARY KEY, name TEXT, age INTEGER
    if not await db.database_exists(schema.db_name):
        raise HTTPException(status_code=404, detail="Database not found, please create the database first.")
    mark = await db.create_table(schema.db_name, schema.table_name, schema.columns)
    if mark:
        return {"message": f"Table {schema.table_name} created successfully in database {schema.db_name}."}
    else:
        return {"message": f"Table '{schema.table_name}' already exists."}

@app.delete("/delete_table/")
async def delete_table(schema: DelTableSchema):
    if not await db.database_exists(schema.db_name):
        raise HTTPException(status_code=404, detail="Database not found.")
    mark = await db.delete_table(schema.db_name, schema.table_name)
    if mark:
        return {"message": f"Table {schema.table_name} deleted successfully from database {schema.db_name}."}
    else:
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}."}

@app.post("/database_exists/{db_name}")
async def database_exists(db_name: str):
    result = await db.database_exists(db_name)
    return result

@app.post("/table_exists/")
async def table_exists(schema: TableExistSchema):
    result = await db.table_exists(schema.db_name, schema.table_name)
    return result

#################################################################
# 一般数据表增删改查
@app.post("/insert_data/")
async def insert_data(schema: InsertDataSchema):
    mark = await db.insert_data(schema.db_name, schema.table_name, schema.columns, schema.values)
    if mark:
        return {"message": "Data inserted successfully."}
    else:
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}, you can create it first."}

@app.put("/update_data/")
async def update_data(schema: UpdateDataSchema):
    if "id" in schema.condition:
        schema.condition = f"id = \"{schema.condition.split('=')[1]}\""
    mark = await db.update_data(schema.db_name, schema.table_name, schema.set_clause, schema.condition)
    if mark:
        return {"message": "Data updated successfully."}
    else:
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}, you can create it first."}

@app.delete("/delete_data/")
async def delete_data(schema: DeleteDataSchema):
    if "id" in schema.condition:
        schema.condition = f"id = \"{schema.condition.split('=')[1]}\""
    mark = await db.delete_data(schema.db_name, schema.table_name, schema.condition)
    if mark:
        return {"message": "Data deleted successfully."}
    else:
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}, you can create it first."}

@app.post("/select_data/")
async def select_data(schema: QueryDataSchema):
    if "id" in schema.condition:
        schema.condition = f"id = \"{schema.condition.split('=')[1]}\""
    logging.info(f"查询条件为：{schema.condition}")
    mark, results = await db.select_data(schema.db_name, schema.table_name, schema.condition)
    if mark:
        if results:
            if "Gender" in schema.condition:
                # 针对直接查询数据库八字的情况
                if schema.sign:
                    logging.info(f"返回数据为:{results[0][3]}")
                    return {"data": results[0][3]}
                else:
                    logging.info(f"返回数据为:{results[0][2]}")
                    return {"data": results[0][2]}
            logging.info(f"返回数据为:{results}")
            return {"data": results}
        else:
            logging.info(f"返回信息为:No {schema.condition} information found in data table {schema.table_name}")
            return {"message": f"No {schema.condition} information found in data table {schema.table_name}"}
    else:
        logging.info(f"返回信息为:The table {schema.table_name} not exist in database {schema.db_name}.")
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}."}

#################################################################
# 对话数据增、查
@app.post("/insert_dialogue/")
async def insert_dialogue(schema: InsertDialogueSchema):
    # columns = "index, user, assistant"
    mark = await db.insert_dialogue(schema.db_name, schema.user_role_id, schema.columns, schema.dialog)
    if mark:
        return {"message": "Data inserted successfully."}
    else:
        return {"message": f"The table {schema.user_role_id} not exist in database {schema.db_name}, you can create it first."}

@app.post("/similar_search/")
async def similar_search(schema: SimilarDataSchema):
    # topk 默认为 3 
    mark, response = await db.similar_search(schema.user_role_id, schema.query, schema.db_name)
    if mark:
        return {"data": response}
    else:
        return {"message": f"Has no dataset name {schema.db_name}, or table {schema.user_role_id} not in dataset {schema.db_name}, or vector dataset {schema.user_role_id + '.index'} has not build, please check again."}

#################################################################
# 提取的重要信息增、查
@app.post("/insert_important_inf/")
async def insert_important_inf(schema: InsertInfSchema):
    mark,response = await db.insert_important_inf(schema.db_name, schema.user_role_id, schema.columns, schema.inf)
    if mark:
        return {"data": response}
    else:
        return {"message": response}

@app.post("/similar_search_inf/")
async def similar_search_inf(schema: SimilarDataSchema):
    # topk 默认为 3 
    mark, response = await db.similar_search_inf(schema.user_role_id, schema.query, schema.db_name)
    if mark:
        return {"data": response}
    else:
        return {"message": f"Has no dataset name {schema.db_name}, or table {schema.user_role_id} not in dataset {schema.db_name}, or vector dataset {schema.user_role_id + '.index'} has not build, please check again."}

#################################################################
# 其他
@app.post("/get_table_structure/")
async def get_table_structure(schema: GetTableStructureSchema):
    result = await db.get_table_structure(schema.db_name, schema.table_name)
    if result:
        return result
    else:
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}."}

if __name__ == "__main__":
    logging.basicConfig(
    level=logging.INFO,  # 确保日志级别设置为INFO
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler()]  # 设定输出到控制台
)
    uvicorn.run(app, host="0.0.0.0", port=8598)
