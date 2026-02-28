import pytz
from datetime import datetime

# 上海时区
SHANGHAI_TZ = pytz.timezone('Asia/Shanghai')

def get_shanghai_now():
    """获取当前上海时区时间"""
    return datetime.now(SHANGHAI_TZ)

def utc_to_shanghai(utc_dt):
    """将UTC时间转换为上海时区时间"""
    if utc_dt is None:
        return None
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    return utc_dt.astimezone(SHANGHAI_TZ)

def shanghai_to_utc(shanghai_dt):
    """将上海时区时间转换为UTC时间"""
    if shanghai_dt is None:
        return None
    if shanghai_dt.tzinfo is None:
        shanghai_dt = SHANGHAI_TZ.localize(shanghai_dt)
    return shanghai_dt.astimezone(pytz.utc)

def format_shanghai_time(dt, fmt='%Y-%m-%d %H:%M:%S'):
    """格式化上海时区时间"""
    if dt is None:
        return '-'
    shanghai_dt = utc_to_shanghai(dt)
    return shanghai_dt.strftime(fmt)
