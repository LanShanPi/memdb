import redis

# 连接 Redis 服务器（dify中的redis）
r = redis.Redis(host='127.0.0.1', port=6379, db=0,password="Test123456")


# 存储用户对话
def store_conversation(user_id, conversation):
    # 使用用户ID作为键，将对话追加到列表中
    r.rpush(f"conversations:{user_id}", conversation)

# 获取用户的固定数量的对话（从末尾开始）
def get_conversations(user_id, num_conversations=10):
    # # num_conversations=3，取出最近的3条对话，默认取最近的10条数据
    # 获取列表的长度
    list_length = r.llen(f"conversations:{user_id}")
    # 防止取的数据条数多于总数据条数
    num_conversations = min(list_length,num_conversations)
    # 计算要提取的起始索引
    start = max(0, list_length - num_conversations)
    end = list_length - 1
    # 取出用户ID对应的对话（从末尾开始，按顺序,start=0,end=-1,就是取全部的数据）
    datas = r.lrange(f"conversations:{user_id}", start, end)
    result = []
    for data in datas: 
        result.append(data.decode('utf-8'))
    return result


# # 示例：存储用户对话
# store_conversation(user_id, "你好啊")
# # 示例：获取用户最近的对话
# num_conversations = 4  # 例如，取出最近的3条对话
# # 列表格式["","",""]
# result = get_conversations(user_id, num_conversations)
