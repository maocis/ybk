import re
import random
from datetime import datetime, timedelta

import bcrypt

from yamo import (
    Document, EmbeddedDocument, IDFormatter, Index,
    BooleanField,
    StringField,
    BinaryField,
    ListField,
    IntField,
    FloatField,
    DateTimeField,
    EmbeddedField,
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
    ymoney = IntField(default=1000)  # Y币
    reserved_ymoney = IntField(default=0)  # 预扣Y币
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


class BankAccount(EmbeddedDocument):

    """ 银行账号 """

    bank = StringField(required=True)  # 建设银行/...
    number = StringField(required=True)
    front = BinaryField()
    back = BinaryField()


class Investor(Document):

    """ 投资人 """

    class Meta:
        idf = IDFormatter('{id_number}')
        idx1 = Index(['user', 'order'], unique=True)

    user = StringField(required=True)  # 用户
    order = IntField(required=True)  # 顺序
    name = StringField(required=True)
    id_type = StringField(required=True)  # 身份证/..
    id_number = StringField(required=True)  # 号码
    id_front = BinaryField()  # 照片
    id_back = BinaryField()
    mobile = StringField(required=True)
    province = StringField(required=True)
    city = StringField(required=True)
    address = StringField(required=True)
    bank_accounts = ListField(EmbeddedField(BankAccount))

    @classmethod
    def get_user_order(cls, user):
        i = cls.query_one({'user': user}, sort=[('order', -1)], limit=1)
        if not i:
            return 1
        else:
            return i.order + 1

    @classmethod
    def user_investors(cls, user):
        return list(cls.query({'user': user}, sort=[('order', 1)]))


class MyPosition(EmbeddedDocument):

    """ 持仓 """
    name = StringField(required=True)
    symbol = StringField(required=True)
    average_price = FloatField(required=True)
    quantity = IntField(required=True)
    price = FloatField(required=True)
    sellable = IntField()
    profit = FloatField()


class MyMoney(EmbeddedDocument):

    """ 资金 """
    usable = FloatField(required=True)
    withdrawable = FloatField(required=True)


class TradeAccount(Document):

    """ 交易账号 """

    class Meta:
        idf = IDFormatter('{exchange}_{login_name}')
        idx1 = Index(['investor', 'exchange'], unique=True)
        idx2 = Index(['exchange', 'login_name'], unique=True)
        idx3 = Index('user')

    user = StringField(required=True)  # 所属用户
    investor = StringField(required=True)  # 投资人
    bank = StringField(required=True)  # 工商银行/...
    exchange = StringField(required=True)  # 交易所简称
    login_name = StringField(required=True)  # 账号
    login_password = StringField(required=False)  # 密码
    money_password = StringField(required=False)  # 资金密码

    verify_message = StringField(default='请先更新状态', required=False)  # 验证失败的原因
    verified = BooleanField(default=False)  # 验证通过
    grab_buy_on = BooleanField(default=False)  # 抢单买
    grab_sell_on = BooleanField(default=False)  # 抢单卖

    position = ListField(EmbeddedField(MyPosition), default=[])
    money = EmbeddedField(MyMoney, default={})

    @classmethod
    def user_accounts(cls, user):
        return list(cls.query({'user': user}))

    @property
    def investor_name(self):
        investors = list(Investor.cached(5).query({'user': self.user}))
        for i in investors:
            if i._id == self.investor:
                return i.name
        else:
            return '未找到'

    @property
    def money_position(self):
        return sum(p.price * p.quantity for p in self.position)
