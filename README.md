1、创建cond环境：
conda create -n memdb python==3.11
pip install -r requirements.txt
1、创建数据库
（1）创建用于八字存储的数据库birthdate,及数据表user_bazi
    运行pre_create.py文件
（2）创建对话历史数据库dialogue（数据表根据项目运行过程中所需进行创建）
    运行pre_create.py文件