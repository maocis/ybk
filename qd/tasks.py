import logging

from invoke import task

from qd.models import exchanges, User, Account

log = logging.getLogger('qd')


@task
def add_user(mobile, username, password, is_admin=None):
    """ 添加用户 """
    try:
        u = User({'mobile': mobile,
                  'username': username,
                  'password': password})
        if is_admin is not None:
            u._is_admin = is_admin
        print(u._data)
        u.upsert()
        log.info('创建/更新用户{}成功!'.format(u._id))
        return True
    except Exception as e:
        log.exception(str(e))
        return False


@task
def add_account(user, exchange, login_name, login_password,
                money_password='', bank_password=''):
    """ 添加账号 """
    try:
        u = User.query_one({'_id': user})
        if not u:
            log.info('找不到用户{}, 无法创建账号'.format(user))
            return False
        if exchange not in exchanges:
            log.info('找不到交易所{}, 无法创建账号'.format(exchange))
            return False
        a = Account({
            'user': user,
            'exchange': exchange,
            'login_name': login_name,
            'login_password': login_password,
            'money_password': money_password,
            'bank_password': bank_password,
        })
        a.upsert()
        log.info('创建/更新账号{}成功'.format(a._id))
        return True
    except Exception as e:
        log.exception(str(e))
        return False
