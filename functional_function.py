import pytz
from datetime import datetime, timedelta
import re
from redis_domain.redis_processer import get_conversations,store_conversation
import sys
sys.path.append(r"/home/kuaipan/memdb/")
from prompt_domain.llm_propmt import Judge_System,Splice_System
from llm_domain.openai_llm import get_openai_response
# chinese_to_digit、parse_relative_date、parse_weekday、parse_days_ago_or_after、parse_day_of_current_month、parse_next_month_day服务于replace_dates_in_sentence

def get_time():
    # 获取上海时间
    local_tz = pytz.timezone('Asia/Shanghai')
    local_time = datetime.now().now(local_tz)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')

def get_time_scope(time_words):
    tz = pytz.timezone('Asia/Shanghai')
    now = datetime.now(tz)
    result = []
    # 现在仅处理“昨天”
    if "昨天" in time_words:
        start_time = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = start_time + timedelta(days=1)
        result.append([start_time.strftime('%Y-%m-%d %H:%M:%S'),end_time.strftime('%Y-%m-%d %H:%M:%S')])
    # 格式为[[start_time,end_time],[]]
    return result

def imformation_processer(id,dialog):
    # 先判断有没有重要信息，是否需要存储
    important_or_not = get_openai_response(dialog,Judge_System)
    if "无重要信息" in important_or_not:
        # 此时不需要存储
        return False,""
    
    # 根据id从redis中获取数据
    num_conversations = 3
    history = get_conversations(id, num_conversations)
    # 对用户说的话进行完善
    query = f"'user_history':{history},'user_new':{dialog}"
    processed_dialog = get_openai_response(query,Splice_System)
    # 将完善后的话存入redis
    store_conversation(id,processed_dialog)
    # 修正关于时间的词
    time_dialog = replace_dates_in_sentence(processed_dialog)
    return True,time_dialog


# 将中文数字转换为阿拉伯数字的函数
def chinese_to_digit(text):
    chinese_num = {
        '零': '0', '一': '1', '二': '2', '三': '3', '四': '4', '五': '5', 
        '六': '6', '七': '7', '八': '8', '九': '9', '十': '10'
    }
    
    # 处理十几到十九的数字
    text = re.sub(r'十([一二三四五六七八九])', lambda x: '1' + chinese_num[x.group(1)], text)
    # 处理二十几到九十九的数字
    text = re.sub(r'([二三四五六七八九])十([一二三四五六七八九]?)', lambda x: chinese_num[x.group(1)] + '0' if x.group(2) == '' else chinese_num[x.group(1)] + chinese_num[x.group(2)], text)
    # 处理十、二十等整数
    text = re.sub(r'十', '10', text)
    
    # 最终处理个位数
    for key, value in chinese_num.items():
        text = text.replace(key, value)
    
    return text

# 解析相对日期（如“今天”、“明天”、“昨天”）
def parse_relative_date(text):
    today = datetime.now()
    if text == "今天":
        return today
    elif text == "明天":
        return today + timedelta(days=1)
    elif text == "后天":
        return today + timedelta(days=2)
    elif text == "昨天":
        return today - timedelta(days=1)
    elif text == "前天":
        return today - timedelta(days=2)
    return None

# 解析“星期X”格式
def parse_weekday(weekday, reference='本'):
    today = datetime.now()
    target_weekday = weekday
    
    if reference == '下':
        days_ahead = target_weekday - today.weekday() + 7
    elif reference == '上':
        days_ahead = target_weekday - today.weekday() - 7
    else:  # '本'星期或者直接'星期X'
        days_ahead = target_weekday - today.weekday()
        if days_ahead < 0:
            days_ahead += 7
    
    return today + timedelta(days=days_ahead)

# 解析“上周X”格式
def parse_last_weekday(weekday):
    today = datetime.now()
    target_weekday = weekday
    days_behind = today.weekday() - target_weekday
    if days_behind < 0:
        days_behind += 7
    days_behind += 7
    return today - timedelta(days=days_behind)

# 解析“X天前”或“X天后”格式
def parse_days_ago_or_after(days, direction):
    today = datetime.now()
    if direction == "前":
        return today - timedelta(days=days)
    elif direction == "后":
        return today + timedelta(days=days)
    return None

# 解析“X号”格式，默认为当前月份
def parse_day_of_current_month(day):
    today = datetime.now()
    return datetime(today.year, today.month, day)

# 解析“上个月”、“下个月”这种表达
def parse_month_reference(reference):
    today = datetime.now()
    year = today.year
    month = today.month

    if reference == '上':
        month -= 1
        if month < 1:
            month = 12
            year -= 1
    elif reference == '下':
        month += 1
        if month > 12:
            month = 1
            year += 1

    return year, month

# 解析“上个月X号”格式
def parse_last_month_day(day):
    today = datetime.now()
    year = today.year
    month = today.month - 1
    if month < 1:
        month = 12
        year -= 1
    return datetime(year, month, day)

# 解析“下个月X号”格式
def parse_next_month_day(day):
    today = datetime.now()
    year = today.year
    month = today.month + 1
    if month > 12:
        month = 1
        year += 1
    return datetime(year, month, day)

# 解析“周末”相关的日期
def parse_weekend(reference='本'):
    today = datetime.now()
    weekday = today.weekday()

    if reference == '本':
        days_to_saturday = (5 - weekday) % 7
        days_to_sunday = (6 - weekday) % 7
    elif reference == '下':
        days_to_saturday = (5 - weekday + 7) % 7
        days_to_sunday = (6 - weekday + 7) % 7
    elif reference == '上':
        days_to_saturday = (5 - weekday - 7) % 7
        days_to_sunday = (6 - weekday - 7) % 7

    saturday = today + timedelta(days=days_to_saturday)
    sunday = today + timedelta(days=days_to_sunday)

    return saturday, sunday

# 解析句子中的时间短语
def replace_dates_in_sentence(sentence):
    # 匹配相对日期
    relative_patterns = {
        r"今天": "今天",
        r"明天": "明天",
        r"后天": "后天",
        r"昨天": "昨天",
        r"前天": "前天"
    }
    
    for pattern, label in relative_patterns.items():
        if re.search(pattern, sentence):
            date = parse_relative_date(label)
            sentence = re.sub(pattern, date.strftime('%Y年%m月%d日'), sentence)

    # 匹配“星期X”或“下星期X”或“上星期X”
    week_days = {
        "一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "天": 6, "日": 6,
        "1": 0, "2": 1, "3": 2, "4": 3, "5": 4, "6": 5, "7": 6
    }
    
    # 解析“星期X”
    match = re.search(r"(上|下)?星期([一二三四五六天日1-7])", sentence)
    if match:
        reference = match.group(1) if match.group(1) else '本'
        weekday = week_days[match.group(2)]
        date = parse_weekday(weekday, reference)
        sentence = re.sub(r"(上|下)?星期([一二三四五六天日1-7])", date.strftime('%Y年%m月%d日'), sentence)

    # 解析“上周X”
    match = re.search(r"上周([一二三四五六天日1-7])", sentence)
    if match:
        weekday = week_days[match.group(1)]
        date = parse_last_weekday(weekday)
        sentence = re.sub(r"上周([一二三四五六天日1-7])", date.strftime('%Y年%m月%d日'), sentence)

    # 匹配“下周X”
    match = re.search(r"下周([一二三四五六天日1-7])", sentence)
    if match:
        weekday = week_days[match.group(1)]
        date = parse_weekday(weekday, reference='下')
        sentence = re.sub(r"下周([一二三四五六天日1-7])", date.strftime('%Y年%m月%d日'), sentence)

    # 匹配“下个月X号”
    match = re.search(r"下个月([一二三四五六七八九十\d]+)号", sentence)
    if match:
        day = int(chinese_to_digit(match.group(1)))
        date = parse_next_month_day(day)
        sentence = re.sub(r"下个月[一二三四五六七八九十\d]+号", date.strftime('%Y年%m月%d日'), sentence)

    # 匹配“上个月X号”
    match = re.search(r"上个月([一二三四五六七八九十\d]+)号", sentence)
    if match:
        day = int(chinese_to_digit(match.group(1)))
        date = parse_last_month_day(day)
        sentence = re.sub(r"上个月[一二三四五六七八九十\d]+号", date.strftime('%Y年%m月%d日'), sentence)

    # 匹配“X天前”或“X天后”
    match = re.search(r"([一二三四五六七八九十\d]+)天(前|后)", sentence)
    if match:
        days = int(chinese_to_digit(match.group(1)))
        direction = match.group(2)
        date = parse_days_ago_or_after(days, direction)
        sentence = re.sub(r"[一二三四五六七八九十\d]+天(前|后)", date.strftime('%Y年%m月%d日'), sentence)

    # 匹配“X号”，默认为当前月份
    match = re.search(r"([一二三四五六七八九十\d]+)号", sentence)
    if match:
        day = int(chinese_to_digit(match.group(1)))
        date = parse_day_of_current_month(day)
        sentence = re.sub(r"[一二三四五六七八九十\d]+号", date.strftime('%Y年%m月%d日'), sentence)
    # 匹配“上个月”、“下个月”
    match = re.search(r"(上|下)个月", sentence)
    if match:
        reference = match.group(1)
        year, month = parse_month_reference(reference)
        sentence = re.sub(r"(上|下)个月", f"{year}年{month}月", sentence)

    # 匹配“周末”、“上周末”、“下周末”
    match = re.search(r"(上|下)?周末", sentence)
    if match:
        reference = match.group(1) if match.group(1) else '本'
        saturday, sunday = parse_weekend(reference)
        weekend_str = f"{saturday.strftime('%Y年%m月%d日')}或{sunday.strftime('%Y年%m月%d日')}"
        sentence = re.sub(r"(上|下)?周末", weekend_str, sentence)

    return sentence
