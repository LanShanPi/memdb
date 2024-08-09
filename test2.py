import requests

# # 创建表
# url = "http://42.123.114.119:8598/create_table/"
# headers = {"Content-Type": "application/json"}
# data = {
#     "db_name": "information",
#     "table_name": "test1",
#     "columns": "inf_id TEXT PRIMARY KEY, inf TEXT, time TEXT"
# }
# response = requests.post(url, headers=headers, json=data)
# # 如果需要查看响应
# status = response.status_code
# result = response.json()  # 如果返回的数据是JSON格式
# if "successfully" in result or "already exists" in result:
#     pass

# # 判断信息重要性
# url = "http://42.123.114.119:8597/chat/"
# headers = {"Content-Type": "application/json"}
# data = {
#     "input": "昨天我去了虹口体育场"
# }
# response = requests.post(url, headers=headers, json=data)
# # 如果需要查看响应
# status = response.status_code
# result = response.json()  # 如果返回的数据是JSON格式
# if "有重要信息" in result["response"]:
#     pass
# else:
#     pass

# # 添加重要信息
# url = "http://42.123.114.119:8598/insert_important_inf/"
# headers = {"Content-Type": "application/json"}
# data = {
#     "db_name": "information",
#     "user_role_id": "test1",
#     "columns": "inf_id,inf,time",
#     "inf": "今天是我生日，我好开心"
# }
# response = requests.post(url, headers=headers, json=data)
# # 如果需要查看响应
# print(response.status_code)
# print(response.json())  # 如果返回的数据是JSON格式


# 查询重要信息
url = "http://42.123.114.119:8598/similar_search_inf/"
headers = {"Content-Type": "application/json"}
data = {
    "db_name": "information",
    "user_role_id": "test1",
    "query": "天为什么是蓝色的"
}
response = requests.post(url, headers=headers, json=data)
# 如果需要查看响应
status = response.status_code
result = response.json()  # 如果返回的数据是JSON格式
# result 格式为：{'data': [['今天是我生日，我好开心', '1.6624228']]}