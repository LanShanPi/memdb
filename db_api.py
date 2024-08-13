from fastapi import FastAPI, HTTPException
from db_schema import *
from typing import List, Any
import os
import database as db
import uvicorn
import logging
import config

app = FastAPI()

# 数据库数据表创、删、查
@app.post("/create_database/{db_name}")
def create_database(db_name: str):
    logging.info("----------create database----------")
    logging.info(f"database id <{db_name}>")
    mark = db.create_database(db_name)
    if mark:
        return {"message": f"Database {db_name} created successfully."}
    else:
        return {"message": f"Database {db_name} already exists."}

@app.delete("/delete_database/{db_name}")
def delete_database(db_name: str):
    mark = db.delete_database(db_name)
    if mark:
        return {"message": f"Database {db_name} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Database not found")
    
    
@app.post("/create_table/")
def create_table(schema: TableSchema):
    # schema.columns:id INTEGER PRIMARY KEY,name TEXT,age INTEGER
    if not db.database_exists(schema.db_name):
        raise HTTPException(status_code=404, detail="Database not found, please create the database first.")
    mark = db.create_table(schema.db_name, schema.table_name, schema.columns)
    if mark:
        return {"message": f"Table {schema.table_name} created successfully in database {schema.db_name}."}
    else:
        return {"message": f"Table '{schema.table_name}' already exists."}
    
@app.delete("/delete_table/")
def delete_table(schema: DelTableSchema):
    if not db.database_exists(schema.db_name):
        raise HTTPException(status_code=404, detail="Database not found.")
    mark = db.delete_table(schema.db_name, schema.table_name)
    if mark:
        return {"message": f"Table {schema.table_name} deleted successfully from database {schema.db_name}."}
    else:
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}."}


@app.post("/database_exists/{db_name}")
def database_exists(db_name: str):
    result = db.database_exists(db_name)
    return result
    # if result:
    #     return {"message":f"The table {db_name} exist."}
    # else:
    #     return {"message":f"The table {db_name} not exist."}

@app.post("/table_exists/")
def table_exists(schema: TableExistSchema):
    result = db.table_exists(schema.db_name, schema.table_name)
    return result
    # if result:
    #     return {"message":f"The table {schema.table_name} exist in database {schema.db_name}."}
    # else:
    #     return {"message":f"The table {schema.table_name} exist in database {schema.db_name}."}


#################################################################
# 一般数据表增删改查
@app.post("/insert_data/")
def insert_data(schema: InsertDataSchema):
    mark = db.insert_data(schema.db_name, schema.table_name, schema.columns, schema.values)
    if mark:
        return {"message": "Data inserted successfully."}
    else:
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}, you can create it first."}

@app.put("/update_data/")
def update_data(schema: UpdateDataSchema):
    if "id" in schema.condition:
        schema.condition = f"id = \"{schema.condition.split('=')[1]}\""
    mark = db.update_data(schema.db_name, schema.table_name, schema.set_clause, schema.condition)
    if mark:
        return {"message": "Data updated successfully."}
    else:
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}, you can create it first."}

@app.delete("/delete_data/")
def delete_data(schema: DeleteDataSchema):
    if "id" in schema.condition:
        schema.condition = f"id = \"{schema.condition.split('=')[1]}\""
    mark = db.delete_data(schema.db_name, schema.table_name, schema.condition)
    if mark:
        return {"message": "Data deleted successfully."}
    else:
        return {"message": f"The table {schema.table_name} not exist in database {schema.db_name}, you can create it first."}

@app.post("/select_data/")
def select_data(schema: QueryDataSchema):
    if "id" in schema.condition:
        schema.condition = f"id = \"{schema.condition.split('=')[1]}\""
    print(schema.condition)
    mark,results = db.select_data(schema.db_name, schema.table_name, schema.condition)
    if mark:
        if results:
            if "Gender" in schema.condition:
                # 针对直接查询数据库八字的情况
                if schema.sign:
                    return {"data":results[0][3]}
                else:
                    return {"data":results[0][2]}
            return {"data": results}
        else:
            return {"message":f"No {schema.condition} information found in data table {schema.table_name}"}
    else:
        return {"message":f"The table {schema.table_name} not exist in database {schema.db_name}."}
#################################################################
# 对话数据增、查
@app.post("/insert_dialogue/")
def insert_dialogue(schema: InsertDialogueSchema):
    # columns = "index,user,assistant"
    mark = db.insert_dialogue(schema.db_name, schema.user_role_id, schema.columns, schema.dialog)
    if mark:
        return {"message": "Data inserted successfully."}
    else:
        return {"message": f"The table {schema.user_role_id} not exist in database {schema.db_name}, you can create it first."}

@app.post("/similar_search/")
def similar_search(schema: SimilarDataSchema):
    # topk 默认为3 
    mark,response = db.similar_search(schema.user_role_id,schema.query,schema.db_name)
    if mark:
        return {"data":response}
    else:
        return {"message":f"Has no dataset name {schema.db_name},or table {schema.user_role_id} not in dataset {schema.db_name}, or vector dataset {schema.user_role_id + '.index'} has not build,please check again."}

#################################################################
# 提取的重要信息增、查
@app.post("/insert_important_inf/")
def insert_important_inf(schema: InsertInfSchema):
    mark = db.insert_important_inf(schema.db_name, schema.user_role_id, schema.columns, schema.inf)
    if mark:
        return {"message": "Data inserted successfully."}
    else:
        return {"message": f"The table {schema.user_role_id} not exist in database {schema.db_name}, you can create it first."}

@app.post("/similar_search_inf/")
def similar_search_inf(schema: SimilarDataSchema):
    # topk 默认为3 
    mark,response = db.similar_search_inf(schema.user_role_id,schema.query,schema.db_name)
    if mark:
        return {"data":response}
    else:
        return {"message":f"Has no dataset name {schema.db_name},or table {schema.user_role_id} not in dataset {schema.db_name}, or vector dataset {schema.user_role_id + '.index'} has not build,please check again."}


#################################################################
# 其他
@app.post("/get_table_structure/")
def get_table_structure(schema: GetTableStructureSchema):
    result = db.get_table_structure(schema.db_name, schema.table_name)
    if result:
        return result
    else:
        return {"message":f"The table {schema.table_name} not exist in database {schema.db_name}."}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8598)
