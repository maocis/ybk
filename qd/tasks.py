import random
import logging
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from invoke import task

from ybk.lighttrade import Trader
from qd.models import (exchanges, User, Account, Exchange,
                       Collection, DailyTrading)


log = logging.getLogger('qd')
executor = ThreadPoolExecutor(10)


def hms():
    d = datetime.utcnow() + timedelta(hours=8)
    return d.hour * 10000 + d.minute * 100 + d.second


def thisdate():
    d = datetime.utcnow() + timedelta(hours=8)
    if hms() < 930:
        d -= timedelta(days=1)
    d = d.replace(hour=0, minute=0, second=0, microsecond=0)
    return d


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


@task
def check_accounts():
    logging.basicConfig(level=logging.ERROR,
                        format='[%(asctime)s] %(name)s'
                        '<%(levelname)s> %(message)s')

    def check_account(account):
        print('检查账号{}_{}'.format(account.exchange,
                                 account.login_name))
        try:
            Trader(account.exchange,
                   account.login_name,
                   account.login_password)
        except:
            pass

    accounts = list(Account.query())
    random.shuffle(accounts)
    for account in accounts:
        executor.submit(check_account, account)


@task
def update_accounts(accounts=None, users=None,
                    exchanges=None, collections=None):
    """ 批量更新账号信息 """
    logging.basicConfig(level=logging.ERROR,
                        format='[%(asctime)s] %(name)s'
                        '<%(levelname)s> %(message)s')

    cond = {}
    if accounts:
        assert isinstance(accounts, list)
        cond['_id'] = {'$in': accounts}
    if users:
        assert isinstance(users, list)
        cond['user'] = {'$in': users}
    if exchanges:
        assert isinstance(exchanges, list)
        cond['exchange'] = {'$in': exchanges}
    if collections:
        assert isinstance(collections, list)
        cond['collections'] = {'$in': collections}

    accounts = list(Account.query(cond))
    random.shuffle(accounts)
    for account in accounts:
        executor.submit(update_account, account)
    executor.shutdown()

    update_users()
    update_exchanges()
    update_collections()


@task
def sync_collections():
    from ybk.config import setup_config
    from ybk.models import Collection as C1
    from ybk.models import Quote as Q1
    setup_config()
    for c in C1.query():
        print(c.exchange, c.symbol)
        td = Q1.count({'exchange': c.exchange,
                       'symbol': c.symbol,
                       'type_': '1d'}) + 1
        if td == 1:
            if not c.offers_at:
                # 没录入过, 基本上会挂
                continue

            # 如果K线不存在, 可能是交易行情无法获取, 直接用估算数字
            td = (datetime.utcnow() - c.offers_at).days - 1

        c2 = Collection({
            'exchange': c.exchange,
            'symbol': c.symbol,
            'name': c.name,
            'trade_day': td,
        })
        c2.upsert()


@task
def update_users(users=None):
    for user in users or [u._id for u in User.query()]:
        update_user(user)


@task
def update_exchanges(exchanges=None):
    for exchange in exchanges or [e._id for e in Exchange.query()]:
        update_exchange(exchange)


@task
def update_collections(collections=None):
    for collection in collections or [c._id for c in Collection.query()]:
        update_collection(collection)


def update_user(user):
    """ 更新用户的账号信息 """
    accounts = list(Account.query({'user': user}))
    u = User.query_one({'_id': user})
    for key, value in accounts_summary(accounts).items():
        setattr(u, key, value)
    u.num_accounts = len(accounts)
    u.num_exchanges = len(set(a.exchange for a in accounts))
    u.upsert()


def update_exchange(exchange):
    """ 更新交易所的账号信息 """
    accounts = list(Account.query({'exchange': exchange}))
    e = Exchange.query_one({'_id': exchange})
    for key, value in accounts_summary(accounts).items():
        setattr(e, key, value)
    e.num_users = len(set(a.user for a in accounts))
    e.num_accounts = len(accounts)
    e.upsert()


def update_collection(collection):
    """ 更新藏品的账号信息 """
    accounts = list(Account.query({'collections': collection}))
    users = set()
    exchange, symbol = collection.split('_')
    name = ''
    quantity = 0
    buy_price = 0
    for account in accounts:
        users.add(account.user)
    summary = accounts_summary(accounts)
    for p in summary['position']:
        if collection.endswith(p.symbol):
            quantity = p.quantity
            buy_price = p.average_price
            name = p.name
            break

    users = list(users)
    c = Collection.query_one({'_id': collection})
    if not c:
        c = Collection({'_id': collection})
    if exchange:
        c.exchange = exchange
    if symbol:
        c.symbol = symbol
    if name:
        c.name = name
    c.users = users or []
    c.accounts = [a._id for a in accounts] or []
    c.quantity = quantity
    c.buy_price = buy_price
    try:
        c.upsert()
    except:
        pass


def update_account(account):
    print('更新账号 {}/{}/{}'.format(account.exchange,
                                 account.login_name,
                                 account.login_password))

    try:
        t = Trader(account.exchange,
                   account.login_name,
                   account.login_password)

        namedict = {c['symbol']: c['name']
                    for c in t.list_collection()}

        money = t.money()['usable']
        profit = 0
        capital = 0
        earned = 0
        lost = 0

        # update position
        position = t.position() or []
        for p in position:
            p['name'] = namedict[p['symbol']]
            profit += p['profit']
            capital += p['amount']

        # update order_status
        order_status = t.order_status() or []
        for o in order_status:
            o['name'] = namedict[o['symbol']]

        # update orders
        orders_dict = {}
        for o in t.orders() or []:
            pair = (o['type_'], o['symbol'])
            if o['profit'] > 0:
                earned += o['profit']
            else:
                lost -= o['profit']
            if pair not in orders_dict:
                o['name'] = namedict[o['symbol']]
                orders_dict[pair] = o
            else:
                o2 = orders_dict[pair]
                amount1 = o.price * o.quantity + \
                    o2.price * o2.quantity
                amount2 = o['current_price'] * o.quantity + \
                    o2['current_price'] * o2.quantity
                o2.quantity += o.quantity
                if o2.quantity:
                    o2.price = amount1 / o2.quantity
                    o2['current_price'] = amount2 / o2.quantity
        orders = list(orders_dict.values())

        cond = {
            'date': thisdate(),
            'account': account._id
        }
        update = {
            'money': money,
            'profit': profit,
            'capital': capital,
            'earned': earned,
            'lost': lost,
            'position': position,
            'orders': orders,
        }
        if order_status:
            # only update when there's order_status
            # because orders will be cleared out after everyday's closing
            update['order_status'] = order_status

        DailyTrading.update_one(cond, {'$set': update}, upsert=True)

        # update collections to acount
        collections = ['{}_{}'.format(account.exchange, p['symbol'])
                       for p in position]
        update['collections'] = collections
        Account.update_one({'_id': account._id},
                           {'$set': update}, upsert=True)
    except Exception as e:
        log.exception(str(e))
        return


def accounts_summary(accounts):
    """ 账号的资金持仓等信息 """
    position_dict = {}
    orders_dict = {}
    order_status = []
    money = 0
    profit = 0
    capital = 0
    earned = 0
    lost = 0
    for account in accounts:
        money += account.money or 0
        profit += account.profit or 0
        capital += account.capital or 0
        earned += account.earned or 0
        lost += account.lost or 0
        for p in account.position:
            if p.symbol not in position_dict:
                position_dict[p.symbol] = p
            else:
                p2 = position_dict[p.symbol]
                price1, quantity1 = p.average_price, p.quantity
                price2, quantity2 = p2.average_price, p2.quantity
                amount = price1 * quantity1 + price2 * quantity2
                quantity = quantity1 + quantity2
                if quantity > 0:
                    p2.quantity = quantity
                    p2.average_price = amount / quantity
                    p2.sellable += p.sellable
                    p2.profit += p.profit
                    p2.amount += p.amount

        for o in account.orders:
            pair = (o.type_, o.symbol)
            if pair not in orders_dict:
                orders_dict[pair] = o
            else:
                o2 = orders_dict[pair]
                amount1 = o.price * o.quantity + \
                    o2.price * o2.quantity
                amount2 = o.current_price * o.quantity + \
                    o2.current_price * o2.quantity
                o2.quantity += o.quantity
                if o2.quantity:
                    o2.price = amount1 / o2.quantity
                    o2.current_price = amount2 / o2.quantity

        for o in account.order_status:
            order_status.append(o)
    return {
        'money': money,
        'profit': profit,
        'capital': capital,
        'position': sorted(position_dict.values(),
                           key=lambda x: x.amount,
                           reverse=True),
        'orders': sorted(orders_dict.values(),
                         key=lambda x: x.profit,
                         reverse=True),
        'order_status': sorted(order_status, key=lambda x: x.order),
    }
