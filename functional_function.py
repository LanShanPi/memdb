import pytz
import datetime

def get_time():
    # 获取上海时间
    local_tz = pytz.timezone('Asia/Shanghai')
    local_time = datetime.datetime.now().now(local_tz)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

def get_time_scope(time):
    pass