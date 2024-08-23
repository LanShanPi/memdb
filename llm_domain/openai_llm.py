from openai import OpenAI
import sys
sys.path.append(r"/home/kuaipan/memdb/")
from config import Base_Url,Api_Key
from prompt_domain.llm_propmt import Judge_System

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

query = "'user_history':['我姓洪'],'user_new':'叫志理'"
system = "请根据user_history中的所有内容，对user_new的内容进行补全，要以第三人称描述的语气总结，如：用户XXX"
print(get_openai_response(query,system))



    
