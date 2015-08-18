# 通讯协议(sysframe)

本文档记录邮币卡交易所客户端的协议(非官方)

本通讯协议适用交易所如下:

'中艺邮币卡', '华中文交所', '金马甲', '江苏文交所', '南方文交所', '宁夏文交所', '福丽特', '华夏文交所', '华强文交所', '南京文交所', '中南文交所', '中融邮币卡', '成都文交所', '南昌文交所'

0. [通用](#common)
0. [下载协议](#download) HTTP/bin
	0. [服务器数据更新](#update)
	0. [交易品种信息](#productinfo)
	0. [日线/分时数据](#history)
0. [行情协议](#quote) TCP/bin
	0. [连接](#connect)
	0. [请求全部最新实时数据](#request)
	0. [服务器时间](#servertime)
	0. [交易时段信息](#tradetime)
	0. [交易行情信息](#tradeinfo)
0. [交易协议](#trade) HTTP/xml
	0. [登陆](#logon) `logon`
	0. [检查用户](#check_user) `check_user`
	0. [修改密码](#change_password) `change_password`
	0. [服务器时间](#sys_time_query) `sys_time_query`
	0. [查询商品信息](#commodity_query) `commodity_query`
	0. [查询市场代码](#market_query) `market_query`
	0. [资金查询](#firm_info) `firm_info`
	0. [持仓查询](#holding_query) `holding_query`
	0. [查询商品盘口](#commodity_data_query) `commodity_data_query`
	0. [买卖下单](#order) `order`
	0. [委托查询](#my_weekorder_query) `my_weekorder_query`
	0. [撤单](#order_wd) `order_wd`
	0. [成交查询](#tradquery) `tradequery`
0. [综合业务](#front)
	0. [出入金(农行/不完整)](#transferabc) `transferabc`
	0. [出入金(其他)](#transfer) `transfer`
	
## <a id="common">通用</a>

连接客户端会有三个服务器端口

- 下载端口(HTTP): 接受一些大文件等适合http传输的东东, 例如交易品种/日线信息等 (HOST1:PORT1)
- 行情端口(TCP): 交换行情数据更新行情信息 (HOST2:PORT2)
- 交易端口(TCP): 用户的登陆退出, 购买等行为 (HOST3:PORT3)

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

## <a id="quote">行情协议</a>

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


## <a id="trade">交易</a>

- 交易API的请求和返回全为xml
- 请求/返回的xml头: <?xml version="1.0" encoding="gb2312"?>
- 以下请求(可)全部使用HTTP 1.1
	- Expect: 100-continue
	- 100 Continue

### <a id="logon">登录logon</a>

- URL: 
	- /issue_tradeweb/httpXmlServlet # 按交易登陆
	- /common_front/checkneedless/user/logon/logon.action # 按综合平台登陆
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=logon
			- USER_ID cn02690000013
			- PASSWORD xxxxxxxx
			- REGISTER_WORD 2015080313411391cn0269000001370822.82989892604
			- // YYYYmmddHHMMSSTTTUSER_ID\d{5}.\d{11}, 和返回的RANDOM_KEY有关
			- // 以下为common_front登陆所需
			- VERSIONINFO
			- LA 0
			- L_M
			- LOGONTYPE pc
- RESPONSE:
	- GNNT
		- REQ name=logon
			- RESULT
				- RETCODE 1187440845777522146 # -> SESSION_ID
				- MESSAGE
				- MODULE_ID 18
				- TYPE
				- LAST_TIME 2015-08-03 13:41:13
				- LAST_IP 116.226.34.73
				- CHG_PWD 2 # 是否更改密码?
				- NAME cn02690000013
				- RANDOM_KEY: 20150809112156776cn0269000001316465.3614295365
				- USER_ID cn02690000013
		
		
### <a id="check_user">检查用户状态</a>

切换功能时需要(ISSUE/FRONTEND)

- URL: 
	- /issue_tradeweb/httpXmlServlet
	- /common_front/checkneedless/user/logon/logon.action
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=check_user
			- USER_ID cn02690000013
			- SESSION_ID 1187440845777522146
			- MODULE_ID 18 # 交易模块?
			- F_LOGONTYPE # pc(综合业务时需要)
			- LOGONTYPE pc
- RESPONSE
	- GNNT
		- REP name=check_user
			- RESULT
				- RETCODE 0
				- MESSAGE
				- MODULE 18 # 交易=18, 综合=99
		
		
### <a id="change_password">修改密码</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=change_password
			- USER_ID 10330008
			- OLD_PASSWORD 111111
			- NEW_PASSWORD caibahaha
			- MODULE_ID 99
			- SESSION_ID 2736065087393846840
- RESPONSE:
    - GNNT
   		- REP name=change_password
   			- RESULT
   				- RETCODE 0
   				- MESSAGE
		
### <a id="sys_time_query">查询系统时间</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST
	- GNNT
		- REQ name=sys_time_query
			- USER_ID 102600012
			- LAST_ID 0
			- SESSION_ID 1167725644699209300
			- CU_LG 0
- RESPONSE
	- GNNT
		- REP name=sys_time_query
			- RESULT
				- RETCODE 0
				- MESSAGE
				- CU_T 10:23:50
				- CU_D 2015-08-09
				- TV_U 1439087030891
				- MARK 0
				- NEW_T 0
				- TD_TTL null
				- TDRP
				- DAY 08


### <a id="commodity_query">藏品查询</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST
	- GNNT
		- REQ name=commodity_query
			- USER_ID cn02690000013
			- SESSION_ID 1187440845777522146
			- COMMODITY_ID # 可为空, 也可为藏品代码
- RESPONSE
	- GNNT
		- REP name=commodity_query
			- RESULT
				- RETCODE 0
				- MESSAGE
			- RESULTLIST
				- REC
					MA_I null
					CO_I 501001
					CO_N 某个名字
					L_SET 2035-07-05 # 最后交易时间
					STA 0 # 正常交易=0, 退市=1, 暂停交易=2
					CT_S 1 # 最小交易单位
					SPREAD 0.1 # 价格变动大小
					MQ 1 # 这个也是最小交易单位?
					SP_U 2687.2 # 最高价
					SP_D 2198.6 # 最低价
					MA_A 1
					BMA 100.0
					SMA 0.0
					BAS 0.0
					SAS 0.0
					PR_C 2442.9 # 现价
					OM 0
					FE_A 1 # 类型, 定价摇号=1
					TE_T 0.1 # 买手续费, percent
					STE_T 0.1 # 卖手续费, percent
					BCHFE 0.0010 # 这一坨应该是手续费
					SCHFE 0.0010
					BCTFE 0.0010
					SCTFE 0.0010
					BCFFE 0.0010
					SCFFE 0.0010
					SFE_A 1 # 手续费算法, 百分比=1, 交易数量=2
					TM_SET 10.0
					STM_SET 10.0
					BRDID 1000
					B_T_M 0
					MAXHOLDDAYS
					
					
### <a id="firm_info">资金信息</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=firm_info
			- USER_ID cn02690000013
			- SESSION_ID 1187440845777522146
- RESPONSE:
	- GNNT
		- REQ name=firm_info
			- RESULT
				- RETCODE 0
				- MESSAGE
			- RESULTLIST
				- REC
					- FI cn02690000013
					- FN 户名
					- TP -1 # 交易分类
					- IF 0.89 # 初始资金(上日资金)
					- IN_F 0 # 入金
					- OU_F 0 # 出金
					- HK_S 0 # 卖出贷款
					- HK_B 0 # 买入贷款
					- IC 0 # 交易手续费
					- UC 0 # 注销服务费
					- IS 0 # 发行服务费
					- SG_F 0 # 申购冻结资金
					- OR_F 0 # 下单冻结资金
					- OT_F 0 # 其他冻结
					- FEE 0 # 当前费用
					- BC_R 0 # 提货注册费
					- BC_U 0 # 提货注销费
					- BC_C 0 # 提货更改费
					- BC_D 0 # 提货配送费
					- SAF 0 # 其他费用
					- OC 0.00 # 其他变化
					- MV 0 # 当前市值
					- UF 0.89 # 日可取资金?
					- DQ 0.89 # 日可用资金
					- JYSQY 0.89 # 当前权益

					
### <a id="market_query">查询市场</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=market_query
			- USER_ID cn02690000013
			- MARKET_ID
			- SESSION_ID 1187440845777522146
- RESPONSE:
	- GNNT
		- REQ name=market_query
			- RESULT
				- RETCODE 0
				- MESSAGE
			- RESULTLIST
				- REC
					- MA_I 99 # 市场号码
					- MA_N # 市场名字
					- STA 1 # 状态 (正常=1)
					- FI_I
					- MAR 1
					- SH_N

### <a id="commodity_data_query">藏品详细查询</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=commodity_data_query
			USER_ID 1026000012
			COMMODITY_ID 99600001 
			SESSION_ID 1167725644699209300
- RESPONSE:
	- GNNT
		- REP name=commodity_data_query
			- RESULT
				- RETCODE 0
				- MESSAGE
			- RESULTLIST
				- REC
					- CO_I 99600001 # 市场+代码
					- CO_N 综合指数
					- L_SET 2025-05-27 # 截止交易日期
					- PR_C 9.95 # 价格
					- BID 10.71 买价 = 买一价
					- BI_D 151 买量 = 买一量
					- OFFER 10.72 # 卖价 = 卖一价
					- OF_D 94 # 卖量 = 卖一量
					- HIGH 10.95 # 最高价
					- LOW 10 # 最低交
					- LAST 10.72 # 上次成交价
					- AVG 10.44 # 均价
					- CHA 0.77 # 涨跌
					- VO_T 51177 # 成交量
					- TT_O 3255112 # 市场总量
					- BP_1 10.71
					- BP_2 10.7
					- BP_3 10.69
					- BP_4 10.68
					- BP_5 10.67
					- SP_1 10.72
					- SP_2 10.73
					- SP_3 10.74
					- SP_4 10.75
					- SP_5 10.76
					- BV_1 151
					- BV_2 111
					- BV_3 10
					- BV_4 100
					- BV_5 100
					- SV_1 94
					- SV_2 290
					- SV_3 300
					- SV_4 100
					- SV_5 1163
					- COUNT 1


### <a id="holding_query">持仓查询</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name="holding_query"
			- USER_ID cn02690000013
			- COMMODITY_ID
			- STARTNUM 0
			- RECCNT 0
			- SESSION_ID 1187440845777522146
			- MARKET_ID
- RESPONSE:
	- GNNT
		- REQ name="holding_query"
			- RESULT
				- RETCODE: -202
				- MESSAGE: 不知道啥错
				- TTLREC: 9
			- RESULTLIST
				- REC
					- CO_I 99100005 
					- CU_I 1000000009013800 # USER_ID + 00
					- BU_H 1 # 持有笔数
					- SE_H 0
					- B_V_H 1 # 可用数量
					- S_V_H 0
					- BU_A 101 # 均价
					- SE_A 0
					- GO_Q 0
					- FL_P 0
					- MAR 101 # 贷款
					- NP_PF 763 # 盈亏
					- MV 864 # 市值
					- LP_R 7.5545 # 涨幅
				


### <a id="order">买卖下单</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=order
			- USER_ID 1026000012
			- CUSTOMER_ID 102600001200 # USER_ID + '00'?
			- BUY_SELL 1 # 买=1, 卖=2
			- COMMODITY_ID 99600001
			- PRICE 10
			- QTY 1
			- SETTLE_BASIS 1
			- CLOSEMODE 0
			- TIMEFLAG 0
			- L_PRICE 0
			- SESSION_ID 1167725644699209300
			- BILLTYPE 0
- RESPONSE:
	- GNNT
		- REP name=order
			- RESULT
				RETCODE 3 # 成功=0
				OR_N 0 # 订单号
				TIME 2015-08-09 10:23:54
				MESSAGE 不在下单时间
				
### <a id="my_weekorder_query">买卖委托查询</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=my_weekorder_query
			- USER_ID 1000000090138
			- BUY_SELL 0 # 不限
			- ORDER_NO 0 # 不限
			- COMMODITY_ID
			- STARTNUM 0 # 起始位置(offset)
			- RECCNT 0 # 记录数(limit)
			- UT 0
			- SESSION_ID 1218796683348049004
			- MARKET_ID
- RESPONSE:
	- GNNT
		- REP name=my_weekorder_query
			- RESULT
				- RETCODE 0
				- MESSAGE
				- TTLREC 1
				- UT 1439099607115 # unix timestamp
			- RESULTLIST
				- REC
					- OR_N 150809008916
					- TIME 2015-08-09 13:53:27
					- STA 1 # 已委托=1, 部分成交=2, 全部成交=3, 全部撤单=5 部分成交后撤单=6
					- TYPE 1 # 买=1, 卖=2
					- SE_F 1 # SettleBasis >.<
					- TR_I 1000000090138 # 交易账号
					- FI_I 1000000090138 # 交易账号
					- CU_I 100000009013800 # +00
					- CO_I 99100035 # 市场号+编码
					- PRI 12.58 # 委托价
					- QTY 1 # 委托量
					- BAL 1 # Balance?
					- L_P 0 # 成交价格?
					- WD_T # 撤单时间
					- C_F # CBasis?
					- B_T_T # BillTradeType?

### <a id="order_wd">撤单</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=order_wd
			- USER_ID 1000000090138
			- ORDER_NO 150809008916
			- SESSION_ID 1218796683348049004
- RESPONSE
	- GNNT
		- REP name=order_wd
			- RESULT
				- RETCODE 0
				- MESSAGE
	

### <a id="tradequery">成交查询</a>

- URL: /issue_tradeweb/httpXmlServlet
- TYPE: POST
- REQUEST:
	- GNNT
		- REQ name=tradequeryy
			- USER_ID 1000000090138
			- LAST_TRADE_ID 0
			- SESSION_ID 1218796683348049004
			- MARKET_ID
- RESPONSE
	- GNNT
		- REP name=tradequery
			- RESULT
				- RETCODE -202 # 没有
				- MESSAGE
			- RESULTLIST
				- REC
					- TR_N 150809009514
					- OR_N 150809010262
					- TI 2015-08-09 14:20:00
					- TY 2 # 买=1, 卖=2
					- SE_F 2
					- FI_I 1000000090138
					- CU_I 100000009013800
					- CO_I 99100028
					- PR 27.05 # 成交价
					- QTY 1 # 成交量
					- O_PR 9.0 # 原价格
					- LIQPL 18.05 # 收益
					- COMM 0.03 # 佣金
					- S_TR_N 12443
					- A_TR_N 7750
					- TR_T 1


### <a id="transferabc">出入金(农行)</a>

正常的post

- URL: /bank_front/bank/money/gotoABCMoneyPage.action
- TYPE: POST
- REQUEST:

	> inoutMoney=0&bankID=05&money=1&cardType=1&password=521710&InOutStart=0&PersonName=&AmoutDate=&BankName=&OutAccount=
	- inoutMoney 0 # 0=出金?
	- bankID 05 # 农行?
	- money 1 # 金额
	- cardType 1 # ?
	- password XXXXX
	- InOutStart 0
	- PersonName 
	- AmountDate
	- BankName
	- OutAccount
- RESPONSE:
	- 返回一个html
	- 弹出U盾验证
	- 验证通过后返回页面


