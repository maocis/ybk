import traceback
from datetime import datetime, timedelta

from models import User, Account, Position, Order, Status
from ybk.lighttrade import Trader

symbols = ['100001', '100002',
           '100010', '100011', '100014', '100019',
           '100020', '100028', '100030',
           '100012', '100015', '10022', '100024']


def update_all_user_accounts():
    for user in User.query():
        try:
            update_user_account(user)
        except:
            traceback.print_exc()


def update_user_account(user):
    position = {}
    orders = {}
    status_list = []
    namedict = {}
    total_money = 0
    for a in Account.query({'user_id': user._id}):
        t = Trader('中港邮币卡', a.login_name, a.login_password)
        if not t.is_logged_in:
            print('{}:{}不是合法账号'.format(a.login_name, a.login_password))
            continue
        if not namedict:
            namedict = {c['symbol']: c['name']
                        for c in t.list_collection()}
        for p in t.position() or []:
            if p['symbol'] not in position:
                position[p['symbol']] = p
                p['name'] = namedict[p['symbol']]
            else:
                p2 = position[p['symbol']]
                price1, quantity1 = p['average_price'], p['quantity']
                price2, quantity2 = p2['average_price'], p2['quantity']
                amount = price1 * quantity1 + price2 * quantity2
                quantity = quantity1 + quantity2
                if quantity > 0:
                    p2['quantity'] = quantity
                    p2['average_price'] = amount / quantity
                    p2['sellable'] = p['sellable']
                    p2['profit'] += p['profit']

        for o in t.orders() or []:
            if (o['type_'], o['symbol']) not in orders:
                orders[(o['type_'], o['symbol'])] = o
                o['name'] = namedict[o['symbol']]
            else:
                o2 = orders[(o['type_'], o['symbol'])]
                price1, quantity1 = o['price'], o['quantity']
                price2, quantity2 = o2['price'], o2['quantity']
                amount = price1 * quantity1 + price2 * quantity2
                quantity = quantity1 + quantity2
                if quantity > 0:
                    o2['quantity'] = quantity
                    o2['price'] = amount / quantity
                    o2['commision'] += o['commision']
                    o2['profit'] += o['profit']

        for s in t.order_status() or []:
            s['name'] = namedict[s['symbol']]
            status_list.append(s)

        total_money += t.money()['usable']

    total_capital = sum(p['price'] * p['quantity']
                        for p in position.values()
                        if p['symbol'] in symbols)
    total_profit = sum(p['profit'] for p in position.values()
                       if p['symbol'] in symbols)

    print(user._id, total_capital, total_profit)

    position_list = sorted(
        position.values(), key=lambda x: x['profit'], reverse=True)
    order_list = sorted(
        orders.values(), key=lambda x: x['profit'], reverse=True)
    status_list = sorted(status_list, key=lambda x: x['order'])

    d = datetime.utcnow() + timedelta(hours=8)
    if d.hour < 9:
        d -= timedelta(days=1)
    d = d.replace(hour=0, minute=0, second=0, microsecond=0)

    Position({
        'user_id': user._id,
        'date': d,
        'position_list': position_list,
    }).upsert()

    Order({
        'user_id': user._id,
        'date': d,
        'order_list': order_list,
    }).upsert()

    if status_list:
        # 有委托单才更新, 以免被覆盖
        Status({
            'user_id': user._id,
            'date': d,
            'status_list': status_list,
        }).upsert()

    user.total_money = total_money
    user.total_capital = total_capital
    user.total_profit = total_profit
    user.upsert()


if __name__ == '__main__':
    update_all_user_accounts()
