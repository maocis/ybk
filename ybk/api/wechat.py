import hashlib

from flask import request, current_app, render_template

from ybk.models import WechatEvent

from .views import api

@api.route('/api/wechat/', methods=['GET', 'POST'])
def wechat():
    """ 接收微信公众号的事件/请求

    - 验证消息真实性
    - 接收浦东消息
    - 接收事件推送
    - 接收语音识别结果

    http://mp.weixin.qq.com/wiki/4/2ccadaef44fe1e4b0322355c2312bfa8.html
    """
    if request.method == 'GET':
        # 验证消息(微信接入)
        token = current_app.config.get('token', '')
        signature = request.args.get('signature', '')
        timestamp = request.args.get('timestamp', '')
        nonce = request.args.get('nonce', '')
        echostr = request.args.get('echostr', '')

        concat = ''.join(sorted([token, timestamp, nonce]))
        sign = hashlib.sha1(concat.encode('utf-8')).hexdigest()
        if sign != signature:
            return render_template('errors/403.html')

        return (echostr, 200)
    elif request.method == 'POST':
        # 其他消息, 直接存了再说
        xml = request.data
        WechatEvent({'xml': xml}).save()
        return ('', 204)
    else:
        # 这个应该不会被执行
        return ('', 204)

