from openai import OpenAI
import sys
sys.path.append(r"/home/kuaipan/memdb/")
from config import Base_Url,Api_Key
from prompt_domain.llm_propmt import Judge_System,Splice_System

client = OpenAI(
    base_url=Base_Url,
    api_key=Api_Key
)

def get_openai_response(query,system,model="gpt-4o-mini"):
    # model="gpt-3.5-turbo",
    # query 类型为：str
    messages = [{"role": "system", "content":system},{"role":"user","content": query}]
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    # 返回类型为str："{'information':'无重要信息'}"
    return response.choices[0].message.content

# query = "'user_history':['我有一个小熊玩具','用户的玩具是一个粉色的小熊。','用户妈妈的名字叫大美','用户的朋友也喜欢用户的粉色小熊玩具。'],'user_new':'就是小明'"
# system = "你是信息拼接高手，你的任务是根据用户的历史记录 user_history 对用户当前说的话 user_new 进行拼接和补充。你需要遵守以下要求：\
#         0、补充的含义是将上下文中的信息补充到当前用户说的话中而非扩写。\
#         1、上下文关联：确保拼接后的内容与用户的历史记录紧密相关，保持逻辑一致。\
#         2、表达流畅：生成的句子应当自然流畅，展示出高超的信息整合能力。\
#         3、意图明确：准确捕捉并反映用户的真实意图，确保输出符合用户的需求。\
#         4、格式要求：所有回复中必须使用“用户XXX”的形式，例如：\
#             用户的名字是洪志理。\
#             用户喜欢的球类运动是打篮球。\
#             用户有个叫王明的朋友。\
#         5、简洁性：不要生成多余的内容，确保所有输出都是相关且必要的。\
#         6、陈述表达：对补充拼接后的内容进行陈述表达，所有的表达都应站在陈述者的角度进行表达，例如：\
#             例如：\
#                 用户的妈妈是李女士。\
#                 用户的爱好是阅读。\
#                 用户的老师是张老师。\
#         7、无关信息处理：当用户说的话与上下文无关或者关系不大时，不进行补充拼接，直接原样输出。\
#         8、在补充拼接信息时，应确保所有事物或活动被明确命名，以提高信息的清晰度。\
# 			例如：\
# 				用户说：“我喜欢打乒乓球。”   应补充为：“用户喜欢的球类运动是打乒乓球。”\
# 				用户说：“我喜欢看电影。”     应补充为：“用户喜欢的娱乐活动是看电影。”\
#                 用户说：“我爸爸叫小帅。”     应补充为：“用户爸爸的名字叫小帅。”\
#         9、补充拼接时要推断用户当前说的话与上下文的联系，根据这种推断来进行补充拼接。\
#         "
## "用户的朋友的名字叫小明。"
# print(get_openai_response(query,system))



    
