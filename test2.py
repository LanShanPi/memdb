from datetime import datetime, timedelta
import pytz
def get_time_scope(time_words):
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    result = []
    # 现在仅处理“昨天”
    if "昨天" in time_words:
        start_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        result.append([start_time.strftime('%Y-%m-%d %H:%M:%S'),end_time.strftime('%Y-%m-%d %H:%M:%S')])
    return result

print(get_time_scope(["昨天"]))