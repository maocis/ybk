import re
import json
from datetime import datetime, timedelta

import requests
import lxml.html

from ybk.log import quote_log as log
from ybk.models import Quote, Collection
from ybk.settings import SITES, get_conf

session = requests.Session()
session.headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36',
    'Accept-Encoding': 'gzip, deflate, sdch',
}


def history_all():
    for site in SITES:
        retries = 3
        while retries > 0:
            retries -= 1
            try:
                history(site)
            except:
                log.exception('站点{}历史行情获取失败, retries={}'.format(site, retries))
            else:
                break


def history(site):
    raise NotImplementedError
