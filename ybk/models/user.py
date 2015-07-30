import re
import random
from datetime import datetime, timedelta

import bcrypt

from yamo import (
    Document, IDFormatter, Index,
    BooleanField,
    StringField,
    DateTimeField,
)


class Code(Document):

    """ 短信验证码 """
    class Meta:
        idx1 = Index(['mobile', 'send_at'])

    mobile = StringField(required=True)
    code = StringField(required=True)
    text = StringField(required=True)
    sent_at = DateTimeField(created=True)

    @classmethod
    def can_create(cls, mobile, type_):
        if not re.compile('^\d{11}$').match(mobile):
            return False, '手机号码格式不正确'

        if type_ == 'register':
            u = User.query_one({'mobile': mobile})
            if u and u.is_active():
                return False, '该手机已注册'

        c = cls.query_one({'mobile': mobile}, sort=[('sent_at', -1)])
        if c and c.sent_at >= datetime.utcnow() - timedelta(seconds=89):
            return False, '发送验证码间隔太频繁'

        return True, ''

    @classmethod
    def create_code(cls, mobile):
        code = '{:06d}'.format(random.randint(0, 999999))
        text = '【{company}】您的验证码是{code}。如非本人操作，请忽略本短信'
        text = text.format(company='邮币卡369',
                           code=code)
        c = cls({'mobile': mobile,
                 'code': code,
                 'text': text})
        c.save()
        return c

    @classmethod
    def verify(cls, mobile, code):
        c = cls.query_one({'mobile': mobile}, sort=[('sent_at', -1)])
        if c:
            if c.sent_at < datetime.utcnow() - timedelta(seconds=60 * 15):
                return False, '验证码超时'
            return c.code == code, '验证码(不)匹配'
        return False, '验证码未发送'


class User(Document):

    """ 用户 """
    class Meta:
        idf = IDFormatter('{mobile}')
        idx1 = Index('mobile', unique=True)
        idx2 = Index('_is_admin')
        idx3 = Index('_is_active')
        idx4 = Index('username', unique=True)

    mobile = StringField(required=True)
    username = StringField()
    password = StringField()    # bcrypt hashed
    invited_by = StringField()  # 邀请人id
    created_at = DateTimeField(created=True)
    last_login_at = DateTimeField(modified=True)

    _is_active = BooleanField(default=False)  # 通过验证
    _is_admin = BooleanField(default=False)

    def add_to_admin(self):
        self._is_admin = True
        self.upsert()
        return True

    def activate(self):
        self._is_active = True
        self.upsert()

    def is_admin(self):
        return self._is_admin

    def is_active(self):
        return self._is_active

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.mobile

    @classmethod
    def check_available(cls, mobile=None, username=None):
        u1 = cls.query_one({'mobile': mobile})
        u2 = cls.query_one({'username': username})
        if u1 or u2:
            return False
        else:
            return True

    @classmethod
    def create_user(cls, mobile, username, password, invited_by):
        if not cls.find_one({'_id': invited_by}):
            raise ValueError('请输入正确的邀请人手机号码')
        if not cls.check_available(mobile, username):
            raise ValueError('手机号码或用户名已被使用')
        u = cls({
            'mobile': mobile,
            'username': username,
            'password': cls.create_password(password),
            'invited_by': invited_by,
        })
        u.save()
        return u

    @classmethod
    def create_password(cls, password):
        return bcrypt.hashpw(password.encode('utf-8'),
                             bcrypt.gensalt()).decode('utf-8')

    @classmethod
    def check_login(cls, mobile, password):
        u = cls.query_one({'mobile': mobile})
        password = password.encode('utf-8')
        if u:
            hashed = u.password.encode('utf-8')
            if bcrypt.hashpw(password, hashed) == hashed:
                return u
        return None
