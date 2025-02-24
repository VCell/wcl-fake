from datetime import datetime, timedelta

def get_server_from_player_guid(guid):
    items = guid.split('-')
    if len(items) != 3:
        return None
    return items[1]

def get_cd_start_time(date_str=None):
    """
    Given a date in '%Y-%m-%d' format, return the most recent Thursday before or on that date.
    If no date is provided, use the current date.

    :param date_str: A string in '%Y-%m-%d' format representing the input date (optional).
    :return: A string in '%Y-%m-%d' format representing the most recent Thursday.
    """
    # If no date string is provided, use the current date
    if date_str is None:
        date = datetime.now()
    else:
        # Parse the date string into a datetime object
        date = datetime.strptime(date_str, '%Y-%m-%d')

    # Thursday is represented by 3 (Monday is 0, Sunday is 6)
    days_behind = (date.weekday() - 3) % 7 
    
    previous_thursday = date - timedelta(days=days_behind)

    # Return the result as a string in '%Y-%m-%d' format
    return previous_thursday.strftime('%Y-%m-%d')

def get_datetime_from_guid(guid) -> datetime:
    """
    根据guid猜实际时间

    :param logtime: Creature-0-4525-603-5075-33186-00005ED33B
    :return :2024-12-15 21:01:47
    """
    spawn_id = int(guid.split('-')[-1], 16)
    MASK = 0x7fffff
    flag_guid = spawn_id & MASK
    cur_time = datetime.now()
    flag_time = int(cur_time.timestamp()) & MASK
    time_offset = 0

    if flag_guid <= flag_time:
        time_offset = flag_guid - flag_time
    else:
        time_offset = flag_guid - (flag_time + MASK + 1)
    dt = datetime.fromtimestamp(cur_time.timestamp() + time_offset)
    return dt

def get_time_string_from_guid(guid) -> str:
    dt = get_datetime_from_guid(guid)
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_pet_uid_from_guid(guid):
    items = guid.split('-')[-1]
    return items[-8:]

def get_datetime_from_logtime(logtime: str) -> datetime:
    """
    根据日志时间猜实际时间

    :param logtime: 12/19 12:40:36.296
    """
    now = datetime.now()
    current_year = now.year
    time_with_year = f"{current_year}/{logtime}"

    parsed_time = datetime.strptime(time_with_year, "%Y/%m/%d %H:%M:%S.%f")
    
    if parsed_time > now:
        parsed_time = parsed_time.replace(year=current_year - 1)
    
    return parsed_time

def ensure_same_value(default, value):
    if default != None:
        assert default == value
    return value