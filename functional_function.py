import pytz
import datetime

def get_time():
    local_tz = pytz.timezone('Asia/Shanghai')
    local_time = datetime.datetime.now().now(local_tz)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')