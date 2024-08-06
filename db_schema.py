from pydantic import BaseModel
from typing import List, Any

class DelTableSchema(BaseModel):
    db_name: str
    table_name: str

class GetTableStructureSchema(BaseModel):
    db_name: str
    table_name: str

class TableExistSchema(BaseModel):
    db_name: str
    table_name: str

class TableSchema(BaseModel):
    db_name: str
    table_name: str
    columns: str

class InsertDataSchema(BaseModel):
    db_name: str
    table_name: str
    columns: str
    values: str

class InsertDialogueSchema(BaseModel):
    db_name: str
    columns: str
    user_role_id: str
    dialog: list

class InsertInfSchema(BaseModel):
    db_name: str
    columns: str
    user_role_id: str
    inf: str

class UpdateDataSchema(BaseModel):
    db_name: str
    table_name: str
    set_clause: str
    condition: str

class DeleteDataSchema(BaseModel):
    db_name: str
    table_name: str
    condition: str

class QueryDataSchema(BaseModel):
    db_name: str
    table_name: str
    condition: str = ""
    sign: bool = False

class SimilarDataSchema(BaseModel):
    user_role_id: str
    query: str
    db_name: str = ""
