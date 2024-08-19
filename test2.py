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


# # 查询重要信息
# url = "http://42.123.114.119:8598/similar_search_inf/"
# headers = {"Content-Type": "application/json"}
# data = {
#     "db_name": "information",
#     "user_role_id": "test1",
#     "query": "天为什么是蓝色的"
# }
# response = requests.post(url, headers=headers, json=data)
# # 如果需要查看响应
# status = response.status_code
# retrieval_result = response.json()  # 如果返回的数据是JSON格式
# # result 格式为：{'data': [['今天是我生日，我好开心', '1.6624228']]}
# if retrieval_result["data"]:
#     prompt_plus = f"注意！'data_add'是根据用户的话从数据库中检索到的数据，请先根据上下文判断这些数据对回复用户的话是否有用，若有用则根据这些数据进行回复，若无用则自己根据用户的话进行回复。data_add：{retrieval_result['data']}."
# print(prompt_plus)


# curl -X POST "http://42.123.114.119:8598/select_data/" -H "Content-Type: application/json" -d '{"db_name":"paipan_data_book","table_name":"paipan","condition":"DateTimeGender = '\''1998-06-19T5:00:00-男'\''"}'
# 查询排盘信息
url = "http://42.123.114.119:8598/select_data/"
headers = {
    "Content-Type": "application/json"
}
data = {
    "db_name": "paipan_data_book",
    "table_name": "paipan",
    "condition": "DateTimeGender = '1998-06-19T5:00:00-男'"
}

response = requests.post(url, headers=headers, json=data)

# 打印响应内容
print(response.text)