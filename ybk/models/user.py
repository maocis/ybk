import random

import bcrypt

from .mangaa import (
    Model,
    IntField,
    BooleanField,
    StringField,
    DateTimeField,
)


class User(Model):

    """ 用户 """
    meta = {
        'idformat': '{mobile}',
        'unique': ['mobile'],
        'indexes': [
            [[('_is_admin', 1)], {}],
            [[('_is_active', 1)], {}],
            [[('mobile', 1)], {'unique': True}],
            [[('username', 1)], {'unique': True}],
        ]
    }
    mobile = StringField()
    username = StringField()
    password = StringField()    # bcrypt hashed
    vcode = StringField()  # 发送的验证码
    created_at = DateTimeField(auto='created')
    last_login_at = DateTimeField(auto='modified')

    _is_active = BooleanField(default=False)  # 通过验证
    _is_admin = BooleanField(default=False)

    def add_to_admin(self):
        self._is_admin = True
        self.save()
        return True

    def activate(self, vcode=None, force=False):
        if vcode == self.vcode or force:
            self._is_active = True
            self.save()
            return True
        else:
            return False

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
        u1 = cls.find_one({'mobile': mobile})
        u2 = cls.find_one({'username': username})
        if u1 or u2:
            return False
        else:
            return True

    @classmethod
    def create_user(cls, mobile, username=None, password=None):
        u = cls({
            'vcode': cls.gen_vcode(),
            'mobile': mobile,
            'username': username,
            'password': cls.create_password(password),
        })
        u.save()
        return u

    @classmethod
    def create_password(cls, password):
        return bcrypt.hashpw(password.encode('utf-8'),
                             bcrypt.gensalt()).decode('utf-8')

    @classmethod
    def check_login(cls, mobile, password):
        u = cls.find_one({'mobile': mobile})
        password = password.encode('utf-8')
        if u:
            hashed = u.password.encode('utf-8')
            if bcrypt.hashpw(password, hashed) == hashed:
                return u
        return None

    @classmethod
    def gen_vcode(cls):
        return '{:06d}'.format(random.randint(0, 999999))
