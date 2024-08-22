import redis

# 连接 Redis 服务器
r = redis.Redis(host='localhost', port=6379, db=0)

# 用户ID
user_id = 'user1'

# 存储用户对话
def store_conversation(user_id, conversation):
    # 使用用户ID作为键，将对话追加到列表中
    r.rpush(f"conversations:{user_id}", conversation)

# 获取用户的固定数量的对话（从末尾开始）
def get_conversations(user_id, num_conversations):
    # 获取列表的长度
    list_length = r.llen(f"conversations:{user_id}")
    # 计算要提取的起始索引
    start = max(0, list_length - num_conversations)
    end = list_length - 1
    # 取出用户ID对应的对话（从末尾开始，按顺序）
    return r.lrange(f"conversations:{user_id}", start, end)

# 示例：存储用户对话
store_conversation(user_id, "你好啊")
store_conversation(user_id, "我姓洪")
store_conversation(user_id, "叫志理")
store_conversation(user_id, "我家河南的")

# 示例：获取用户最近的对话
num_conversations = 4  # 例如，取出最近的3条对话
conversations = get_conversations(user_id, num_conversations)

dialog = []
for conv in conversations:
    dialog.append(conv.decode('utf-8'))

print(dialog)
