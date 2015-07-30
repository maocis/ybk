from datetime import datetime, timedelta

import requests

import ybk.config

from yamo import (
    Document, IDFormatter, Index,
    IntField,
    StringField,
    DateTimeField,
)


class WechatAccessToken(Document):

    """ 微信ACCESS_TOKEN """
    class Meta:
        idf = IDFormatter('{access_token}')
        idx1 = Index('expires_at', expireAfterSeconds=7200)

    access_token = StringField(required=True)
    expires_in = IntField()
    expires_at = DateTimeField(required=True)
    updated_at = DateTimeField(modified=True)

    @classmethod
    def get_access_token(cls):
        instance = cls.query_one()
        if instance:
            return instance['access_token']
        else:
            appid = ybk.config.conf.get('wechat_appid')
            appsecret = ybk.config.conf.get('wechat_appsecret')
            grant_type = 'client_credential'
            url = 'https://api.weixin.qq.com/cgi-bin/token'
            params = {
                'grant_type': grant_type,
                'appid': appid,
                'secret': appsecret,
            }
            j = requests.get(url, params=params, timeout=(3, 7)).json()
            expires_at = datetime.utcnow() + timedelta(seconds=j['expires_in'])
            cls({'access_token': j['access_token'],
                 'expires_in': j['expires_in'],
                 'expires_at': expires_at}).save()
            return j['access_token']


class WechatEvent(Document):

    """ 微信事件

    暂时只保存, 不处理
    """
    xml = StringField()  # xml格式数据主题
    updated_at = DateTimeField(modified=True)
