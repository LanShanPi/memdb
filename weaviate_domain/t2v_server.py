# /home/kuaipan/model/t2v/text2vec-base-chinese

from fastapi import FastAPI, Request
from text2vec import SentenceModel
import os
import logging

# 设置环境变量来指定使用的 GPU
os.environ['CUDA_VISIBLE_DEVICES'] = "0"

# 初始化 FastAPI 应用
app = FastAPI()

# 加载 SentenceModel 模型
model = SentenceModel('/home/kuaipan/model/t2v/text2vec-base-chinese')

# 定义请求的结构
@app.post("/embed")
async def embed(request: Request):
    # 从请求中获取 JSON 数据
    data = await request.json()
    sentences = data.get("sentences", [])
    logging.info(f"请求数据为：{sentences}")
    # 生成嵌入
    # 向量长度为768
    embeddings = model.encode(sentences)
    # 将嵌入结果返回为 JSON 格式
    return {"embeddings": embeddings.tolist()}

# 运行应用程序
if __name__ == "__main__":
    import uvicorn
    logging.basicConfig(
    level=logging.INFO,  # 确保日志级别设置为INFO
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[logging.StreamHandler()]  # 设定输出到控制台
)
    uvicorn.run(app, host="0.0.0.0", port=12306)

