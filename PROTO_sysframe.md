# 通讯协议(sysframe)

本文档记录邮币卡交易所客户端的协议(非官方)

本通讯协议适用交易所如下:

'中艺邮币卡', '华中文交所', '金马甲', '江苏文交所', '南方文交所', '宁夏文交所', '福丽特', '华夏文交所', '华强文交所', '南京文交所', '中南文交所', '中融邮币卡', '成都文交所', '南昌文交所'

0. [通用](#common)
0. [下载协议](#download)
	0. [服务器数据更新](#update)
	0. [交易品种信息](#productinfo)
	0. [日线/分时数据](#history)
0. [行情协议](#trade)
	0. [连接](#connect)
	0. [请求全部最新实时数据](#request)
	0. [服务器时间](#servertime)
	0. [交易时段信息](#tradetime)
	0. [交易行情信息](#tradeinfo)
0. [用户协议](#user)

## <a id="common">通用</a>

连接客户端会有三个服务器端口

- 下载端口(HTTP): 接受一些大文件等适合http传输的东东, 例如交易品种/日线信息等 (HOST1:PORT1)
- 行情端口(TCP): 交换行情数据更新行情信息 (HOST2:PORT2)
- 用户端口(TCP): 用户的登陆退出, 购买等行为 (HOST3:PORT3)

## <a id="downlaod">下载协议</a>

### <a id="update">服务器数据更新</a>

更新配置信息, 如IP地址等, 并不是太重要, 先略过

### <a id="xmlclass">交易品XML数据</a>

`http://HOST1:PORT1/hqApplet/data/CreateXMLClass.xml`

内容是个简单的两层XML, 前两层是一个list, 第三层有各种信息, 一般有以下这些

- `cc_commodity_id`
- `cc_desc`
- `cc_fullname`
- `cc_name`
- `cc_pricetype`
- `cc_remark`
- `cc_market_name`
- `cc_market`

### <a id="productinfo">交易品种信息</a>

更新交易所的交易品种一览, 包括藏品代码, 藏品名称, 藏品简称等

`http://HOST1:PORT1/hqApplet/data/productinfo.dat`


```py
>>> url = 'http://www.cacecybk.com.cn:16914/hqApplet/data/productinfo.dat'
>>> r = requests.get(url)
>>> binascii.hexify(r.content[:150])
b'03 0133795 d000165d 00000000d'
 '0004313030300002303000000000000ce'
 '7bbbce59088e68c87e695b00000000200'
 '023030000230300000000200045a485a5'
 '300045a475a5300000004000000010000'
 '000200000003000000043c23d70a'
 '0006353031303031000230303f8000000'
 '015e4ba8ce78988e4ba8ce58886e995bf'
 'e58fb7e588b80000000a0002303000023'
 '030000000030007...'
```

以下为16进制表示的代码(金马甲)

```
03            协议头
01 33 79 5d   日期, !i, 20150617
00 00 16 5d   时间, !i, 150000
00 00 00 0d   信息的条数, 以下是信息正文, 重复0d次

  00 04         编码长度
  31 30 30 30   藏品代码(1000)
  00 02 30 30   ?
  00 00 00 00   ?
  00 0c         名称长度
  e7bbbce59088e68c87e695b utf-8编码的名字
  00 00 00 02   长度
    00 02 30 30   ?
    00 02 30 30   ?
  00 00 00 02   简称的个数
    00 04 简称长度
    5a 48 5a 53  简称的字母
    00 04 简称长度
    5a 47 5a 53  简称的字母
  00 00 00 04 数数的个数
    00 00 00 01
    00 00 00 02
    00 00 00 03
    00 00 00 04
  3c 23 d7 0a 浮点数0.001, 手续费?

```


### <a id="history">日线/分时数据</a>

下载日线/分时数据

- 日线

```py
url = 'http://HOST1:PORT1/hqApplet/data/day/00{}.day.zip'.format(symbol)
content = gzip.decompress(requests.get(url).content)
```

内容的格式

```bash
04 00 00 00 # 日线/分钟线个数

	XX XX XX XX  数字日期, 180626[1450]
	XX XX XX XX  高 >f 
	XX XX XX XX  开
	XX XX XX XX  低
	XX XX XX XX  收
	XX XX XX XX  平均
	XX XX XX XX  ？
	XX XX XX XX  成交量
	XX XX XX XX  成交额
	XX XX XX XX  藏品总库存
```

## <a id="trade">行情协议</a>

### <a id="connect">1. 连接</a>

```py
import socket
s = socket.socket()
s.connect((HOST2, PORT2))
```

连接后, 服务器端会先发送当前服务器时间和交易时段信息, 然后不停地更新最新交易数据过来，只需要不停地recv就行了

```py
s.recv(8192)
```

也可以主动发送内容给服务器端


### <a id="request">2. 请求当前全部品种的数据</a>

指令码: 0x0d, 后面参数意义不详

```py
s.send(b'\x0d' + b'\x00\x00\x00\x00')
```

### <a id="servertime">3. 服务器时间</a>

```
09 协议码
00 02 30 30 ?
01 33 79 5d 日期, !i, 20150607
00 00 16 5d 时间, !i, 152246
```

### <a id="tradetime">4. 交易时间</a>

```
08 协议码
00 00 00 01 ?
00 02 30 30 ?
00 00 00 02 区段个数

  00 00 00 01 第几段
  XX XX XX XX 起始年月日, !i, 20150616
  XX XX XX XX 起始时分, !i, 930
  XX XX XX XX 终止年月日, !i, 20150616
  XX XX XX XX 终止时分, !i, 1130
  XX XX XX XX 年月日
  00 00 00 01 ?

  ...

0c ? 
00 00 00 00 ?
00 00 00 00 ?
00 f0 00 00 ?
00 00 ?
```

### <a id="tradeinfo">5. 行情信息</a>

```
05 协议码
00 00 00 0d 行情的条数
  
  00 02 30 30 ?
  00 06 代码长度
  2  1  3  0  1  8 代码
  D  a2 d4 cd 昨收, !f
  D  99 y  ec 开盘, !f
  D  93 a0 00 最高, !f
  D  99 y  ec 收盘, !f
  00 00 00 00 ?
  00 00 01 <  成交量, !i
  A  17 ea 00 e0 00 00 00 成交金额 !d
  00 00 00 01 现量, !i
  c1 e4 92 J  委比, !f
  =  d5 `  #  量比, !f
  D  9a fc cd 均价, !f
  00 00 e  90 库存, !i
  00 00 00 03 买量, !i
  00 00 00 05 卖量, !i
  D  99 a0 00 买价, !f
  D  9e a0 00 卖价, !f
  00 00 结束符?
  
  ... 
```