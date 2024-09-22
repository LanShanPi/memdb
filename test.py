# import re
# from datetime import datetime, timedelta

# # 将中文数字转换为阿拉伯数字的函数
# def chinese_to_digit(text):
#     chinese_num = {
#         '零': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', 
#         '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
#     }
    
#     # 处理十几到十九的数字
#     text = re.sub(r'十([一二三四五六七八九])', lambda x: '1' + chinese_num[x.group(1)], text)
#     # 处理二十几到九十九的数字
#     text = re.sub(r'([二三四五六七八九])十([一二三四五六七八九]?)', lambda x: chinese_num[x.group(1)] + '0' if x.group(2) == '' else chinese_num[x.group(1)] + chinese_num[x.group(2)], text)
#     # 处理十、二十等整数
#     text = re.sub(r'十', '10', text)
    
#     # 最终处理个位数
#     for key, value in chinese_num.items():
#         text = text.replace(key, value)
    
#     return text

# # 解析相对日期（如“今天”、“明天”、“昨天”）
# def parse_relative_date(text):
#     today = datetime.now()
#     if text == "今天":
#         return today
#     elif text == "明天":
#         return today + timedelta(days=1)
#     elif text == "后天":
#         return today + timedelta(days=2)
#     elif text == "昨天":
#         return today - timedelta(days=1)
#     elif text == "前天":
#         return today - timedelta(days=2)
#     return None

# # 解析“星期X”格式
# def parse_weekday(weekday, reference='本'):
#     today = datetime.now()
#     target_weekday = weekday
    
#     if reference == '下':
#         days_ahead = target_weekday - today.weekday() + 7
#     elif reference == '上':
#         days_ahead = target_weekday - today.weekday() - 7
#     else:  # '本'星期或者直接'星期X'
#         days_ahead = target_weekday - today.weekday()
#         if days_ahead < 0:
#             days_ahead += 7
    
#     return today + timedelta(days=days_ahead)

# # 解析“上周X”格式
# def parse_last_weekday(weekday):
#     today = datetime.now()
#     target_weekday = weekday
#     days_behind = today.weekday() - target_weekday
#     if days_behind < 0:
#         days_behind += 7
#     days_behind += 7
#     return today - timedelta(days=days_behind)

# # 解析“X天前”或“X天后”格式
# def parse_days_ago_or_after(days, direction):
#     today = datetime.now()
#     if direction == "前":
#         return today - timedelta(days=days)
#     elif direction == "后":
#         return today + timedelta(days=days)
#     return None

# # 解析“X号”格式，默认为当前月份
# def parse_day_of_current_month(day):
#     today = datetime.now()
#     return datetime(today.year, today.month, day)

# # 解析“上个月”、“下个月”这种表达
# def parse_month_reference(reference):
#     today = datetime.now()
#     year = today.year
#     month = today.month

#     if reference == '上':
#         month -= 1
#         if month < 1:
#             month = 12
#             year -= 1
#     elif reference == '下':
#         month += 1
#         if month > 12:
#             month = 1
#             year += 1

#     return year, month

# # 解析“上个月X号”格式
# def parse_last_month_day(day):
#     today = datetime.now()
#     year = today.year
#     month = today.month - 1
#     if month < 1:
#         month = 12
#         year -= 1
#     return datetime(year, month, day)

# # 解析“下个月X号”格式
# def parse_next_month_day(day):
#     today = datetime.now()
#     year = today.year
#     month = today.month + 1
#     if month > 12:
#         month = 1
#         year += 1
#     return datetime(year, month, day)

# # 解析“周末”相关的日期
# def parse_weekend(reference='本'):
#     today = datetime.now()
#     weekday = today.weekday()

#     if reference == '本':
#         days_to_saturday = (5 - weekday) % 7
#         days_to_sunday = (6 - weekday) % 7
#     elif reference == '下':
#         days_to_saturday = (5 - weekday + 7) % 7
#         days_to_sunday = (6 - weekday + 7) % 7
#     elif reference == '上':
#         days_to_saturday = (5 - weekday - 7) % 7
#         days_to_sunday = (6 - weekday - 7) % 7

#     saturday = today + timedelta(days=days_to_saturday)
#     sunday = today + timedelta(days=days_to_sunday)

#     return saturday, sunday

# # 解析句子中的时间短语
# def replace_dates_in_sentence(sentence):
#     # 匹配相对日期
#     relative_patterns = {
#         r"今天": "今天",
#         r"明天": "明天",
#         r"后天": "后天",
#         r"昨天": "昨天",
#         r"前天": "前天"
#     }
    
#     for pattern, label in relative_patterns.items():
#         if re.search(pattern, sentence):
#             date = parse_relative_date(label)
#             sentence = re.sub(pattern, date.strftime('%Y年%m月%d日'), sentence)

#     # 匹配“星期X”或“下星期X”或“上星期X”
#     week_days = {
#         "一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "天": 6, "日": 6,
#         "1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6
#     }
    
#     # 解析“星期X”
#     match = re.search(r"(上|下)?星期([一二三四五六天日1-7])", sentence)
#     if match:
#         reference = match.group(1) if match.group(1) else '本'
#         weekday = week_days[match.group(2)]
#         date = parse_weekday(weekday, reference)
#         sentence = re.sub(r"(上|下)?星期([一二三四五六天日1-7])", date.strftime('%Y年%m月%d日'), sentence)

#     # 解析“上周X”
#     match = re.search(r"上周([一二三四五六天日1-7])", sentence)
#     if match:
#         weekday = week_days[match.group(1)]
#         date = parse_last_weekday(weekday)
#         sentence = re.sub(r"上周([一二三四五六天日1-7])", date.strftime('%Y年%m月%d日'), sentence)

#     # 匹配“下周X”
#     match = re.search(r"下周([一二三四五六天日1-7])", sentence)
#     if match:
#         weekday = week_days[match.group(1)]
#         date = parse_weekday(weekday, reference='下')
#         sentence = re.sub(r"下周([一二三四五六天日1-7])", date.strftime('%Y年%m月%d日'), sentence)

#     # 匹配“下个月X号”
#     match = re.search(r"下个月([一二三四五六七八九十\d]+)号", sentence)
#     if match:
#         day = int(chinese_to_digit(match.group(1)))
#         date = parse_next_month_day(day)
#         sentence = re.sub(r"下个月[一二三四五六七八九十\d]+号", date.strftime('%Y年%m月%d日'), sentence)

#     # 匹配“上个月X号”
#     match = re.search(r"上个月([一二三四五六七八九十\d]+)号", sentence)
#     if match:
#         day = int(chinese_to_digit(match.group(1)))
#         date = parse_last_month_day(day)
#         sentence = re.sub(r"上个月[一二三四五六七八九十\d]+号", date.strftime('%Y年%m月%d日'), sentence)

#     # 匹配“X天前”或“X天后”
#     match = re.search(r"([一二三四五六七八九十\d]+)天(前|后)", sentence)
#     if match:
#         days = int(chinese_to_digit(match.group(1)))
#         direction = match.group(2)
#         date = parse_days_ago_or_after(days, direction)
#         sentence = re.sub(r"[一二三四五六七八九十\d]+天(前|后)", date.strftime('%Y年%m月%d日'), sentence)

#     # 匹配“X号”，默认为当前月份
#     match = re.search(r"([一二三四五六七八九十\d]+)号", sentence)
#     if match:
#         day = int(chinese_to_digit(match.group(1)))
#         date = parse_day_of_current_month(day)
#         sentence = re.sub(r"[一二三四五六七八九十\d]+号", date.strftime('%Y年%m月%d日'), sentence)
#     # 匹配“上个月”、“下个月”
#     match = re.search(r"(上|下)个月", sentence)
#     if match:
#         reference = match.group(1)
#         year, month = parse_month_reference(reference)
#         sentence = re.sub(r"(上|下)个月", f"{year}年{month}月", sentence)

#     # 匹配“周末”、“上周末”、“下周末”
#     match = re.search(r"(上|下)?周末", sentence)
#     if match:
#         reference = match.group(1) if match.group(1) else '本'
#         saturday, sunday = parse_weekend(reference)
#         weekend_str = f"{saturday.strftime('%Y年%m月%d日')}或{sunday.strftime('%Y年%m月%d日')}"
#         sentence = re.sub(r"(上|下)?周末", weekend_str, sentence)

#     return sentence


# # 示例输入
# sentences = [
#     "上个月三号我去了旅游。",
#     "上个月5号我去了医院。",
#     "下个月三号我想去玩。",
#     "下个月3号我想去玩。",
#     "下个月十五号有个会议。",
#     "下个月十三号有个活动。",
#     "我今天想去理发。",
#     "我昨天去吃面了。",
#     "我们下周三开会。",
#     "我们上周五开会。",
#     "我前天刚回来。",
#     "他3天前出发的。",
#     "二十号是我的生日。",
#     "十号我要去医院。",
#     "下星期二我要开会。",
#     "上星期五我去过那里。",
#     "星期日我们去爬山。",
#     "星期1要交作业。",
#     "我们这周末去度假。",
#     "上周末我在家休息。",
#     "下周末我们有安排。",
#     "你好啊小明",
#     "昨天是星期1",
#     "上个月我去了旅游。",
#     "下个月我会搬家。"
# ]

# # 输出解析和替换结果
# for sentence in sentences:
#     replaced_sentence = replace_dates_in_sentence(sentence)
#     print(f"原句: {sentence}")
#     print(f"转换后的句子: {replaced_sentence}\n")


# import sqlite3

# # 连接到 SQLite 数据库
# # 如果数据库文件不存在，它会自动创建
# conn = sqlite3.connect('/home/kuaipan/disk1/db_domain/paipan_data_book.db')

# # 创建一个游标对象
# cursor = conn.cursor()

# # 执行查询，获取数据库中的所有表
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

# # 获取查询结果
# tables = cursor.fetchall()

# # 输出表的名称
# for table in tables:
#     print(table[0])

# # 关闭游标和连接
# cursor.close()
# conn.close()




# import sqlite3

# # 连接到 SQLite 数据库
# conn = sqlite3.connect('/home/kuaipan/disk1/db_domain/large_data_1970_2020.db')

# # 创建一个游标对象
# cursor = conn.cursor()

# # 执行修改表名的 SQL 语句
# old_table_name = 'large_data_table'  # 原表名
# new_table_name = 'paipan'  # 新表名

# try:
#     cursor.execute(f"ALTER TABLE {old_table_name} RENAME TO {new_table_name};")
#     print(f"表名已从 '{old_table_name}' 修改为 '{new_table_name}'")
# except sqlite3.Error as e:
#     print(f"修改表名时出错: {e}")

# # 提交更改并关闭游标和连接
# conn.commit()
# cursor.close()
# conn.close()




# import sqlite3

# # 连接到 SQLite 数据库
# conn = sqlite3.connect('/home/kuaipan/disk1/db_domain/paipan_data_book.db')

# # 创建一个游标对象
# cursor = conn.cursor()

# # 要查看数据结构的表名
# table_name = 'paipan'

# # 执行查询，获取表的数据结构
# cursor.execute(f"PRAGMA table_info({table_name});")

# # 获取查询结果
# columns = cursor.fetchall()

# # 输出表的结构
# print(f"结构信息：{table_name}")
# for column in columns:
#     print(f"列ID: {column[0]}, 列名: {column[1]}, 数据类型: {column[2]}, 是否允许NULL: {column[3]}, 是否为主键: {column[5]}")

# # 关闭游标和连接
# cursor.close()
# conn.close()



# import requests

# url = "http://42.123.114.119:8598/select_data/"
# headers = {
#     "Content-Type": "application/json"
# }

# data = {
#     "db_name": "paipan_data_book",
#     "table_name": "paipan",
#     "condition": "DateTimeGender = '1998-06-19T5:00:00-男'"
# }

# response = requests.post(url, headers=headers, json=data)

# # 输出响应内容
# print(response.text)


# import random
# def main(arg):
#     prompt = "你是role1，你现在要扮演一个捧哏的角色，根据role2为用户的测算面向用户说一些附和的话，下面是测算内容："
#     if arg.split("：") == "财宝仙翁":
#         role_list = ["学运仙子","前程仙官","桃花仙子","灵啊"]
#         num_elements = random.randint(0, 1)
#         result = random.sample(role_list, num_elements)
#         if result:
#             return {
#                 "prompt":prompt.replace("role1",result[0]).replace("role2","财宝仙翁")
#                 }
#         else:
#             return {
#                 "prompt":None
#                 }
#     elif arg.split("：") == "学运仙子":
#         role_list = ["财宝仙翁","前程仙官","桃花仙子","灵啊"]
#         num_elements = random.randint(0, 1)
#         result = random.sample(role_list, num_elements)
#         if result:
#             return {
#                 "prompt":prompt.replace("role1",result[0]).replace("role2","学运仙子")
#                 }
#         else:
#             return {
#                 "prompt":None
#                 }
#     elif arg.split("：") == "前程仙官":
#             role_list = ["财宝仙翁","学运仙子","桃花仙子","灵啊"]
#             num_elements = random.randint(0, 1)
#             result = random.sample(role_list, num_elements)
#             if result:
#                 return {
#                     "prompt":prompt.replace("role1",result[0]).replace("role2","前程仙官")
#                     }
#             else:
#                 return {
#                     "prompt":None
#                     }
#     elif arg.split("：") == "桃花仙子":
#         role_list = ["财宝仙翁","前程仙官","学运仙子","灵啊"]
#         num_elements = random.randint(0, 1)
#         result = random.sample(role_list, num_elements)
#         if result:
#             return {
#                 "prompt":prompt.replace("role1",result[0]).replace("role2","桃花仙子")
#                 }
#         else:
#             return {
#                 "prompt":None
#                 }

# import random

# def random_selection(lst):
#     # 根据指定概率选择0或1
#     num_elements = random.choices([0, 1], weights=[0.4, 0.6])[0]
#     return random.sample(lst, num_elements)

# # 示例列表
# my_list = ['元素1', '元素2', '元素3', '元素4']

# # 随机选择0或1个元素
# selected_elements = random_selection(my_list)
# print(selected_elements)

import redis

# 连接 Redis 服务器
r = redis.Redis(host='127.0.0.1', port=6379, db=0,password="Test123456")
r.ping()
print("成功")