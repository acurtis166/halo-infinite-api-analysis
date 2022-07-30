
import os
import pkgutil
from typing import Generator
import yaml, re
from yaml.loader import SafeLoader
import datetime as dt


def get_package_data(rel_file_path:str):

    return pkgutil.get_data('haloinfinite', rel_file_path)


def load_config(file_name='config.yaml') -> dict:

    with open(file_name) as fp:
        return yaml.load(fp, SafeLoader)


def batch(iterable, n:int=1) -> Generator:

    l = len(iterable)
    for i in range(0, l, n):
        yield iterable[i:min(i + n, l)]


def find(lst, key, value):

    for i, dic in enumerate(lst):
        if dic[key] == value:
            return i
    return None


def unwrap_xuid(xuid:str) -> str:

    return xuid[5:-1] if xuid[0] == 'x' else xuid


def wrap_xuid(xuid:str) -> str:

    return xuid if xuid[0] == 'x' else f'xuid({xuid})'


def unwrap_bot_id(bid:str) -> str:

    return bid[4:-1] if bid[0] == 'b' else bid


def wrap_bot_id(bid:str) -> str:

    return bid if bid[0] == 'b' else f'bid({bid})'


def parse_iso_duration(duration:str) -> float:
    """Parse week, day, hour, minute, and second components from an ISO8601 duration string into seconds.

    Args:
        duration (float): ISO8601 duration string, e.g. P1DT1H7M51.1385037S

    Returns:
        float: duration in seconds
    """

    def try_float(s:str, default:float=0):
        if s is None:
            return default
        try:
            return float(s[:-1])
        except ValueError:
            return default

    p = re.compile('^P(\d+[.]?\d*Y)?(\d+[.]?\d*M)?(\d+[.]?\d*W)?(\d+[.]?\d*D)?T?(\d+[.]?\d*H)?(\d+[.]?\d*M)?(\d+[.]?\d*S)?$')
    m = p.match(duration)
    if m is None:
        raise ValueError('Duration could not be parsed: {}'.format(duration))

    # get values for all the components
    yrs = try_float(m.group(1))
    mnths = try_float(m.group(2))
    wks = try_float(m.group(3))
    days = try_float(m.group(4))
    hrs = try_float(m.group(5))
    mins = try_float(m.group(6))
    secs = try_float(m.group(7))

    if yrs > 0 or mnths > 0:
        raise ValueError('Duration must be an ISO8601 duration string without a year or month component: {}'.format(duration))

    # create a timedelta from components and return the duration as seconds
    td = dt.timedelta(weeks=wks, days=days, hours=hrs, minutes=mins, seconds=secs)
    return td.total_seconds()


def get_available_cpu_count():

    # TODO return available, not physical
    return os.cpu_count()