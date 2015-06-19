from datetime import datetime, timedelta

import requests

import ybk.config

from .mangaa import (
    Model,
    IntField,
    StringField,
    DateTimeField,
)


class WechatAccessToken(Model):

    """ 微信ACCESS_TOKEN """

    meta = {
        'idformat': 'access_token',
        'indexes': [
            [[('expires_at', 1)], {'expireAfterSeconds': 0}],
        ],
    }
    access_token = StringField()
    expires_in = IntField()
    expires_at = DateTimeField()
    updated_at = DateTimeField(auto='modified')

    @classmethod
    def get_access_token(cls):
        instance = cls.find_one()
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


class WechatEvent(Model):

    """ 微信事件

    暂时只保存, 不处理
    """
    xml = StringField()  # xml格式数据主题
    updated_at = DateTimeField(auto='modified')
