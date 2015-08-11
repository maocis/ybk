# 宗易汇API

0. [准备](#prepare)
0. [通用设定](#common)
0. [功能分类](#functions)
0. [APIS](#apis)


## <a id="prepare">准备</a>

- 安装宗易汇: http://123.57.218.62:30300/filestore/apks/zongyihui.apk
	- 交易: http://123.57.218.62:30300/filestore/apks/Issue.apk
	- 出入金: http://123.57.218.62:30300/filestore/apks/BankInterface.apk
	- 行情: http://123.57.218.62:30300/filestore/apks/QuotationF.apk
- 首次登陆绑定手机号
- 记录PINSCODE: `jingchao146810398069841090`

## <a id="common">通用设定</a>


- 交互URL: `http://m.zongyihui.cn:30200/nuclear/communicateServlet`
- 所有交互都是POST操作，POST一个xml
- Headers:
	- User-Agent: Dalvik/1.6.0 (Linux; U; Android 4.4.4; Samsung Galaxy S5 - 4.4.4 - API 19 - 1080x1920 Build/KTU84P)
	- Content-Type: text/xml
	- Accept-Encoding: gzip
	- Accept: */*
- 返回结果格式为html/xml


## <a id="functions">功能分类</a>

- 启动应用
	0. [启动设备](#startdevice) `startdevice`
	0. [欢迎页面](#getwelcomepage) `getwelcomepage`
	0. [系统版本](#getversion) `getversion`
	0. [检查app登录状态](#checkpins) `checkpins`
	0. [通知推送](#sendnotice) `sendnotice`
	0. [查询宗易汇模块](#trademodelinfo) `trademodelinfo`
	0. [是否已登录app](#islogon) `islogon`
	0. [退出app](#logout) `logout`

- 绑定交易所
	0. [查询可绑市场](#marketinfo) `marketinfo`
	0. [绑定市场](#bind) `bind`
	0. [解除绑定](#unbind) `unbind`

- 登录登出交易所
	0. [获得市场的交易服务器](#tradeserverinfo) `tradeserverinfo`
	0. [从交易服务器获得交易加密信息](#encryptstr) `encryptstr`
	0. [用交易加密信息登陆](#user_login) `user_login`
	0. [从交易所登出](#marketlogout) `marketlogout`
	0. [用户登出](#user_logoff) `user_logoff`

- 交易相关
	0. [交易所时间](#sys_time_query) `sys_time_query`
	0. [可交易商品查询](#query_commodity) `query_commodity`
	0. [检查用户](#check_user) `check_user` ??
	0. [获得发送类型](#get_delivery_type) `get_delivery_type` ??
	0. [商品盘口查询](#commodity_data_query) `commodity_data_query`
	0. [查看可买卖数量](#query_buy_or_sell_quantity) `query_buy_or_sell_quantity`
	0. [买入/卖出商品](#order_submit) `order_submit`
	0. [委托查询](#my_order_query) `my_order_query`
	0. [撤销委托](#order_cancel) `order_cancel`
	0. [成交查询](#query_trade) `query_trade`

- 申购发行
 	0. [申购列表](#issue_commodity) `issue_commodity`
 	0. [申购详细信息](#issue_commodity_detail) `issue_commodity_detail`
 	0. [申购下单](#issue_order) `issue_order`
 	0. [申购委托查询](#issue_order_query) `issue_order_query`
 	0. [申购中签查询](#issue_trade_query) `issue_trade_query`

- 资金持仓
	0. [持仓查询](#holding_query) `holding_query`
	0. [持仓详细查询](#holding_details_query) `holding_details_query`
	0. [资金汇总信息](#firm_info) `firm_info`

- 行情
	0. [行情服务器](#quotationserverinfo) `quotationserverinfo`
	0. [用户信息](#getcustominfo) `getcustominfo`
	0. 


## <a id="workflow">APIs</a>

### 获取连接Session

### 查看可绑定

### <a id="bind">绑定市场</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="bind">
    <MARKETID>19</MARKETID>
    <PASSWORD>caibahaha</PASSWORD>
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>152770231198432777</SESSIONID>
    <TRADEMODELID>1</TRADEMODELID>
    <TRADERID>800059800</TRADERID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="bind">
    <result>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```

### <a id="tradeserverinfo">获得交易服务器</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="tradeserverinfo">
    <MARKETID>19</MARKETID>
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>152770231198432777</SESSIONID>
    <TRADEMODELID>1</TRADEMODELID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS>
  <REP name="tradeserverinfo">
    <RESULTLIST>
      <REC>
        <TRADENAME>???׷?????</TRADENAME>
        <TRADEURL>http://218.246.20.84:16940/Issue4ariesMobileServer/communicateServlet</TRADEURL>
      </REC>
    </RESULTLIST>
    <RESULT>
      <RETCODE>0</RETCODE>
      <MESSAGE/>
    </RESULT>
  </REP>
</MEBS>
```

### <a id="encryptstr">获得加密信息</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="encryptstr">
    <MARKETID>19</MARKETID>
    <PASSWORD>caibahaha</PASSWORD>
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>152770231198432777</SESSIONID>
    <TRADERID/>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="encryptstr">
    <result>
      <encryption>42355253301754163622418004734470245359314066038829224905546112632704529409444867254047537179874886117823760549252518002392950460186618343835153366569243146328170385049569862936515440866564835289496949715635553098088086013343837346662101406500030156284800910398074219841577741748994298483662949707299915002764</encryption>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```

### <a id="user_login">登陆</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="user_login">
    <IC>42355253301754163622418004734470245359314066038829224905546112632704529409444867254047537179874886117823760549252518002392950460186618343835153366569243146328170385049569862936515440866564835289496949715635553098088086013343837346662101406500030156284800910398074219841577741748994298483662949707299915002764</IC>
    <PASSWORD>caibahaha</PASSWORD>
    <RANDOM_KEY/>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="user_login">
    <result>
      <module_id>18</module_id>
      <last_time>2015-08-06 15:07:56</last_time>
      <last_ip>116.226.34.73</last_ip>
      <chg_pwd>0</chg_pwd>
      <name>800059800</name>
      <random_key>2015080616325453780005980054781.4734595751</random_key>
      <retcode>154319795346981014</retcode>
    </result>
  </rep>
</mebs_mobile>
```

### <a id="trademodelinfo">宗易汇模块查询</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="trademodelinfo">
    <MARKETID>19</MARKETID>
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>152770231198432777</SESSIONID>
  </REQ>
</MEBS_MOBILE>
```

- 返回
	- 7: 发行申购?
	- 6: 出入金?
	- 100: 行情?

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS>
  <REP name="trademodelinfo">
    <RESULTLIST>
      <REC>
        <TRADEMODELID>1</TRADEMODELID>
        <NAME>Ͷ??Ʒ</NAME>
        <ACTION>gnnt.MEBS.Issue.Activity.Action.WelcomeActivity</ACTION>
        <ICOURL>/images/trademodel/41.png</ICOURL>
        <VERSIONNO>9</VERSIONNO>
        <PKGNAME>gnnt.MEBS.Issue</PKGNAME>
        <FORCEDUPDATE>N</FORCEDUPDATE>
        <UPDATEURL>/apks/Issue.apk</UPDATEURL>
        <MODULEID>7</MODULEID>
        <SERVICENAME>gnnt.MEBS.Issue.service.PluginService</SERVICENAME>
      </REC>
      <REC>
        <TRADEMODELID>6</TRADEMODELID>
        <NAME>?????</NAME>
        <ACTION>gnnt.MEBS.BankInterface.Activity.action.WelcomeActivity</ACTION>
        <ICOURL>/images/trademodel/42.png</ICOURL>
        <VERSIONNO>10</VERSIONNO>
        <PKGNAME>gnnt.MEBS.BankInterface</PKGNAME>
        <FORCEDUPDATE>N</FORCEDUPDATE>
        <UPDATEURL>/apks/BankInterface.apk</UPDATEURL>
        <MODULEID>5</MODULEID>
        <SERVICENAME>gnnt.MEBS.BankInterface.service.PluginService</SERVICENAME>
      </REC>
      <REC>
        <TRADEMODELID>100</TRADEMODELID>
        <NAME>????ϵͳ</NAME>
        <ACTION>gnnt.MEBS.QuotationF.Activitys.Action.WelcomeActivity</ACTION>
        <ICOURL>/images/quotation/43.png</ICOURL>
        <VERSIONNO>12</VERSIONNO>
        <PKGNAME>gnnt.MEBS.QuotationF</PKGNAME>
        <FORCEDUPDATE>Y</FORCEDUPDATE>
        <UPDATEURL>/apks/QuotationF.apk</UPDATEURL>
      </REC>
    </RESULTLIST>
    <RESULT>
      <RETCODE>0</RETCODE>
      <MESSAGE/>
    </RESULT>
  </REP>
</MEBS>
```

### <a id="query_commodity">可交易商品查询</a>

- 请求
	- S_I: 登陆的`retcode`
	- U: 账号
	- `COMMODITY_ID`: 可添加指定商品如211004

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="query_commodity">
    <COMMODITY_ID/>
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回
	- RESULT
		- RETCODE
		- MESSAGE
		- TTLREC
	- RESULTLIST
		- REC
			- BRF: 仓单注册费用(Bill)
			- BURF: 仓单注销费用(Bill)
			- CO_I: 代码
			- CO_N: 名称
			- CT_S: 交易单位(个) 
			- FE_A: 类型, 1=竞价委托?
			- IFR: 发行服务费
			- L_SET: 最后交易日
			- O_QTY: 已发货量
			- PR_C: 上次结算价格
			- QTY: 总发行量
			- SCE: 卖手续费(%)
			- SFE_A: 手续费算法(1=百分比)
			- SPREAD: 最小变动单位
			- SP_D: 当日下限价格
			- SP_U: 当日上限价格
			- STA: 状态(0=当前有效)
			- TE_T: 买手续费(%)

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REP name="query_commodity">
    <RESULTLIST>
      <REC>
        <CO_I>211004</CO_I>
        <CO_N>????ţ??</CO_N>
        <L_SET>2050-05-07</L_SET>
        <STA>0</STA>
        <CT_S>1</CT_S>
        <SPREAD>0.01</SPREAD>
        <SP_U>98.44</SP_U>
        <SP_D>85.02</SP_D>
        <PR_C>89.49</PR_C>
        <FE_A>1</FE_A>
        <TE_T>0.1</TE_T>
        <SCE>0.1</SCE>
        <SFE_A>1</SFE_A>
        <BRF>0.0</BRF>
        <BURF>0.0</BURF>
        <QTY>1</QTY>
        <O_QTY>0</O_QTY>
        <IFR>0.0</IFR>
      </REC>
...
```


### <a id="sys_time_query">服务器时间查询</a>

在交易模块时10秒钟查询一次

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="sys_time_query">
    <CU_LG>1</CU_LG>
    <LAST_ID/>
    <S_I>154319795346981014</S_I>
    <TD_CNT/>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回
	- tv_u: timestamp (ms)

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="sys_time_query">
    <result>
      <cu_t>16:32:54</cu_t>
      <cu_d>2015-08-06</cu_d>
      <tv_u>1438849974765</tv_u>
      <new_t>0</new_t>
      <td_ttl>0</td_ttl>
      <day>06</day>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs_mobile>
```

### <a id="get_delivery_type">发送类型查询(这啥?)</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="get_delivery_type">
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REP name="">
    <RESULT>
      <RETCODE>-1</RETCODE>
      <MESSAGE>???? xml ????ʧ??</MESSAGE>
    </RESULT>
  </REP>
</MEBS_MOBILE>
```

### <a id="commodity_data_query">商品盘口查询</a>

在交易模块时2秒钟请求一次

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="commodity_data_query">
    <COMMODITY_ID>211004</COMMODITY_ID>
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回	
	- BS: 依次为 买一卖一, 买二卖二, 买三卖三
	- BQ: 买量
	- BP: 买价
	- SQ: 卖量
	- SP: 卖价

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REP name="commodity_data_query">
    <RESULTLIST>
      <REC>
        <CO_I>211004</CO_I>
        <CO_N>????ţ??</CO_N>
        <HIGH>90.70</HIGH>
        <LOW>88.02</LOW>
        <LAST>89.50</LAST>
        <CHA>0.01</CHA>
        <BSL>
          <BS>
            <BQ>8.00</BQ>
            <BP>88.88</BP>
            <SQ>20.00</SQ>
            <SP>89.49</SP>
          </BS>
          <BS>
            <BQ>164.00</BQ>
            <BP>88.62</BP>
            <SQ>59.00</SQ>
            <SP>89.50</SP>
          </BS>
          <BS>
            <BQ>90.00</BQ>
            <BP>88.61</BP>
            <SQ>1.00</SQ>
            <SP>89.51</SP>
          </BS>
        </BSL>
      </REC>
      ...
    </RESULTLIST>
    <RESULT>
      <TTLREC>1</TTLREC>
      <RETCODE>0</RETCODE>
      <MESSAGE/>
    </RESULT>
  </REP>
</MEBS_MOBILE>
```

### <a id="check_user">检查用户</a>

在主页面时三分钟请求一次

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="check_user">
    <MODULE_ID>18</MODULE_ID>
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="check_user">
    <result>
      <module_id>18</module_id>
      <retcode>154319795346981014</retcode>
    </result>
  </rep>
</mebs_mobile>
```


### <a id="holding_query">持仓查询</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="holding_query">
    <COMMODITY_ID/>
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="holding_query">
    <resultlist>
      <rec>
        <co_i>918602</co_i>
        <se_h>11</se_h>
        <s_v_h>11</s_v_h>
        <bu_a>3.5</bu_a>
        <mar>38.5</mar>
        <np_pf>191.84</np_pf>
        <mv>230.34</mv>
      </rec>
      <rec>
        <co_i>918603</co_i>
        <se_h>321</se_h>
        <s_v_h>321</s_v_h>
        <bu_a>0.3</bu_a>
        <mar>96.3</mar>
        <np_pf>1338.57</np_pf>
        <mv>1434.87</mv>
      </rec>
    </resultlist>
    <result>
      <ttlrec>5</ttlrec>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs_mobile>
```

### <a id="my_order_query">委托列表</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="my_order_query">
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
    <UT>0</UT>
  </REQ>
</MEBS_MOBILE>
```


- 返回
	- RESULT
		- MESSAGE
		- RETCODE
		- TTLREC 有效时间(?) = 下次刷新间隔?
		- UT 更新时间
	- RESULTLIST
		- REC
			- BAL  balance
			- CO_I 代码
			- OR_N 订单号
			- PRI 订单价格
			- QTY 订单数量
			- STA 状态=?(1=已委托,2=部分成交,3=全部成交,5=全部撤单,6=部分成交后撤单)
			- TIME 下单时间
			- TYPE 买卖类型(1=买, 2=卖)
			- WD_T 撤单时间

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="my_order_query">
    <result>
      <ttlrec>0</ttlrec>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs_mobile>
```

### <a id="islogon">是否已登录</a>

登陆2小时后检查

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="islogon">
    <SESSIONID>152770231198432777</SESSIONID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="islogon">
    <result>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```

### <a id="firm_info">当日资金汇总</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="firm_info">
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REP name="firm_info">
    <RESULT>
      <FI>800059800</FI>
      <FN>??????</FN>
      <TP>-1</TP>
      <IF>816.11</IF>
      <IN_F>0</IN_F>
      <OU_F>0</OU_F>
      <HK_S>0</HK_S>
      <IC>0</IC>
      <UC>0</UC>
      <HK_B>0</HK_B>
      <OR_F>0</OR_F>
      <OT_F>0</OT_F>
      <IS>0</IS>
      <FEE>0</FEE>
      <BC_R>0</BC_R>
      <BC_U>0</BC_U>
      <BC_C>0</BC_C>
      <BC_D>0</BC_D>
      <SAF>0</SAF>
      <OC>0.00</OC>
      <MV>2513.93</MV>
      <SG_F>0</SG_F>
      <UF>816.11</UF>
      <DQ>816.11</DQ>
      <JYSQY>3330.04</JYSQY>
      <RETCODE>0</RETCODE>
      <MESSAGE/>
    </RESULT>
  </REP>
</MEBS_MOBILE>
```

### <a id="query_trade">成交查询</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="query_trade">
    <LAST_TRADE_ID/>
    <RECCNT>20</RECCNT>
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回
	- RESULT
		- RETCODE
		- MESSAGE
		- REW
		- TTLREC
	- RESULTLIST
		- REC    
			- COMM: 佣金, double
			- CO_I: 代码
			- LIQPL: 卖出盈亏
			- OR_N: 订单号码
			- O_PR: 成本价
			- PR: 价格
			- QTY: 数量
			- TI: 成交时间 %Y-%m-%d %H:%M:%S
			- TR_N: 交易号码
			- TY: 买卖(1=买,2=卖)
		

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="query_trade">
    <resultlist/>
    <result>
      <ttlrec>0</ttlrec>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs_mobile>
```

### <a id="holding_details_query">持仓详细查询</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="holding_details_query">
    <COMMODITY_ID/>
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="holding_details_query">
    <resultlist>
      <rec>
        <co_i>917804</co_i>
        <se_h>121</se_h>
        <bu_a>0.3</bu_a>
        <mar>36.3</mar>
      </rec>
      <rec>
        <co_i>918004</co_i>
        <se_h>100</se_h>
        <bu_a>0.3</bu_a>
        <mar>30</mar>
      </rec>
      <rec>
        <co_i>918603</co_i>
        <se_h>321</se_h>
        <bu_a>0.3</bu_a>
        <mar>96.3</mar>
      </rec>
    </resultlist>
    <result>
      <ttlrec>5</ttlrec>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs_mobile>
```


### <a id="issue_commodity">申购列表查询</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="issue_commodity">
    <C_I/>
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REP name="issue_commodity">
    <RESULTLIST>
      <REC>
        <CO_I>223003</CO_I>
        <CO_N>????20?????</CO_N>
        <BR>fxhy</BR>
        <PRC>350.00</PRC>
        <QTY>2000.00</QTY>
        <S_D>2015-08-06</S_D>
        <E_D>2015-08-06</E_D>
      </REC>
      <REC>
        <CO_I>644901</CO_I>
        <CO_N>?????????10Ԫ??</CO_N>
        <BR>fxhy</BR>
        <PRC>10.00</PRC>
        <QTY>67950.00</QTY>
        <S_D>2015-08-06</S_D>
        <E_D>2015-08-06</E_D>
      </REC>
      <REC>
        <CO_I>629403</CO_I>
        <CO_N>????ԴС????</CO_N>
        <BR>fxhy</BR>
        <PRC>16.00</PRC>
        <QTY>64822.00</QTY>
        <S_D>2015-08-06</S_D>
        <E_D>2015-08-06</E_D>
      </REC>
    </RESULTLIST>
    <RESULT>
      <TTLREC>3</TTLREC>
      <RETCODE>0</RETCODE>
      <MESSAGE/>
    </RESULT>
  </REP>
</MEBS_MOBILE>
```


### <a id="issue_order_query">申购委托查询</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="issue_order_query">
    <E_D>2015-08-06</E_D>
    <S_D>2015-08-06</S_D>
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回
	- RESULT
		- MESSAGE
		- RETCODE
		- TTLREC
	- RESULTLIST
		- REC
			- BACK_IC: 后端总费用
			- BACK_ICF:后端服务费
			- B_D: 开始日期
			- CO_I: 代码
			- CO_N: 名称
			- E_N: 结束序号
			- IC: 总费用
			- ICF: 服务费
			- OR_N: 订单号码
			- PRI: 价格
			- QTY: 数量
			- STA: 状态
			- S_N: 开始序号
			- TIME: 下单时间

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="issue_order_query">
    <resultlist/>
    <result>
      <ttlrec>0</ttlrec>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs_mobile>
```

### <a id="issue_order_query">申购中签查询</a>

- 请求

<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="issue_trade_query">
    <E_D>2015-08-06</E_D>
    <S_D>2015-08-06</S_D>
    <S_I>154319795346981014</S_I>
    <U>800059800</U>
  </REQ>
</MEBS_MOBILE>

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="issue_trade_query">
    <resultlist/>
    <result>
      <ttlrec>0</ttlrec>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs_mobile>
```

### <a id="versioninfo">模块版本查询</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="versioninfo">
    <MARKETID>-1</MARKETID>
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>152770231198432777</SESSIONID>
    <TRADEMODELID>6</TRADEMODELID>
    <VERSIONNO>0</VERSIONNO>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS>
  <REP name="versioninfo">
    <RESULTLIST>
      <REC>
        <VERSIONNO>2</VERSIONNO>
        <UPGRADEINFO>1 ???????棻</UPGRADEINFO>
      </REC>
      <REC>
        <VERSIONNO>3</VERSIONNO>
        <UPGRADEINFO>1 ???????棻</UPGRADEINFO>
      </REC>
      <REC>
        <VERSIONNO>4</VERSIONNO>
        <UPGRADEINFO>1 ???Ƹ?ϵͳ?л?????</UPGRADEINFO>
      </REC>
      <REC>
        <VERSIONNO>5</VERSIONNO>
        <UPGRADEINFO>1 ????ϵͳ?л?????</UPGRADEINFO>
      </REC>
      <REC>
        <VERSIONNO>6</VERSIONNO>
        <UPGRADEINFO>1 ?????л?????</UPGRADEINFO>
      </REC>
      <REC>
        <VERSIONNO>7</VERSIONNO>
        <UPGRADEINFO>?޸??ʽ???ˮ??ѯ??ע??Ϣ??ʾ????</UPGRADEINFO>
        <VERSIONNAME>F1.0.6</VERSIONNAME>
      </REC>
      <REC>
        <VERSIONNO>8</VERSIONNO>
        <UPGRADEINFO> </UPGRADEINFO>
        <VERSIONNAME>F1.0.7</VERSIONNAME>
      </REC>
      <REC>
        <VERSIONNO>9</VERSIONNO>
        <UPGRADEINFO>1 ?Ż?ϵͳ??ѯ?ٶȣ? 2 ????ϵͳͼƬ</UPGRADEINFO>
        <VERSIONNAME>F1.0.8</VERSIONNAME>
      </REC>
      <REC>
        <VERSIONNO>10</VERSIONNO>
        <UPGRADEINFO>1 ?ڲ?????ˮ??¼??ʱ???жϱ?עΪ?յ??????2 ?û?????????????߷????????????⣬??????ȷ??ʾ??</UPGRADEINFO>
        <VERSIONNAME>F1.0.9</VERSIONNAME>
      </REC>
    </RESULTLIST>
    <RESULT>
      <RETCODE>0</RETCODE>
      <MESSAGE/>
    </RESULT>
  </REP>
</MEBS>
```


### <a id="quotationserverinfo">行情服务器</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="quotationserverinfo">
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>199542258327141326</SESSIONID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS>
  <REP name="quotationserverinfo">
    <RESULTLIST>
      <REC>
        <IP>118.145.4.148</IP>
        <NAME>??ͨ</NAME>
        <SOCKETPORT>40600</SOCKETPORT>
        <HTTPPORT>40700</HTTPPORT>
      </REC>
      <REC>
        <IP>115.182.221.26</IP>
        <NAME>????</NAME>
        <SOCKETPORT>40600</SOCKETPORT>
        <HTTPPORT>40700</HTTPPORT>
      </REC>
    </RESULTLIST>
    <RESULT>
      <RETCODE>0</RETCODE>
      <MESSAGE/>
    </RESULT>
  </REP>
</MEBS>
```

### <a id="marketinfo">查询可绑市场</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="marketinfo">
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>199542258327141326</SESSIONID>
    <STATUS>2</STATUS>
    <TRADEMODELID>1</TRADEMODELID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS>
  <REP name="marketinfo">
    <RESULTLIST>
      <REC>
        <MARKETID>1</MARKETID>
        <MARKETNAME>?Ͼ??Ľ???</MARKETNAME>
        <LOGO>/images/market/market_1/logo_655.png</LOGO>
        <MARKETURL>http://123.57.218.62:30300/filestore/images/market/market_1/introduction.html</MARKETURL>
        <STATUS>1</STATUS>
        <TRADERID/>
        <ADDUSERURL>http://180.97.2.74:16908/SelfOpenAccount/mobile/register_broker.jsp</ADDUSERURL>
      </REC>
      <REC>
        <MARKETID>4</MARKETID>
        <MARKETNAME>????????????</MARKETNAME>
        <LOGO>/images/market/market_4/logo_646.png</LOGO>
        <MARKETURL>http://123.57.218.62:30300/filestore/images/market/market_4/introduction.html</MARKETURL>
        <STATUS>1</STATUS>
        <TRADERID/>
      </REC>
    </RESULTLIST>
    <RESULT>
      <RETCODE>0</RETCODE>
      <MESSAGE/>
    </RESULT>
  </REP>
</MEBS>
```

### <a id="bind">解除绑定</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="unbind">
    <MARKETID>19</MARKETID>
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>199542258327141326</SESSIONID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="unbind">
    <result>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```

### <a id="logout">退出登录</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="logout">
    <SESSIONID>199542258327141326</SESSIONID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="logout">
    <result>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```

### <a id="sendnotice">推送通知</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="sendnotice">
    <NOTICEID>0</NOTICEID>
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>517659447167919617</SESSIONID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="sendnotice">
    <resultlist/>
    <result>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```


### <a id="getversion">获得版本号</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="getversion">
    <FRAMEVERSIONNO>13</FRAMEVERSIONNO>
    <MARKETID>-1</MARKETID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="getversion">
    <result>
      <forcedupdate>N</forcedupdate>
      <frameversionno>13</frameversionno>
      <updateurl>http://123.57.218.62:30300/filestore</updateurl>
      <frameupdatepath>/apks/zongyihui.apk</frameupdatepath>
      <versionname>F1.1.2</versionname>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```

### <a id="getwelcomepage">欢迎界面</a>

- 请求

```xml 
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="getwelcomepage">
    <DEV>ad000000000000000</DEV>
    <MAR>-1</MAR>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="getwelcomepage">
    <result>
      <welurl/>
      <time>0</time>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```

### <a id="startdevice">启动设备</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="startdeviceinfo">
    <BRAND>generic</BRAND>
    <DEVICEID>ad000000000000000</DEVICEID>
    <DEVICETYPE>2</DEVICETYPE>
    <MARKETID>-1</MARKETID>
    <MODEL>Samsung Galaxy S5 - 4.4.4 - API 19 - 1080x1920</MODEL>
    <NETPROVIDER/>
    <NETWORKTYPE>WIFI</NETWORKTYPE>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="startdeviceinfo">
    <result>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```


### <a id="checkpins">检查app状态</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="checkpins">
    <DEVICEID>ad000000000000000</DEVICEID>
    <PINSCODE>jingchao146810398069841090</PINSCODE>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="checkpins">
    <result>
      <userid>jingchao</userid>
      <name>jingchao</name>
      <phone>13611825698</phone>
      <mail>scv2duke@163.com</mail>
      <retcode>517659447167919617</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```

### <a id="query_buy_or_sell_quantity">查询可买卖数量</a>

请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="query_buy_or_sell_quantity">
    <COMMODITY_ID>17106082</COMMODITY_ID>
    <DIRECTION>1</DIRECTION>
    <PRICE>5400</PRICE>
    <S_I>527178095144368734</S_I>
    <U>1001000208</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="query_buy_or_sell_quantity">
    <result>
      <quantity>0</quantity>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs_mobile>
```


### <a id="order_submit">买入/卖出</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="order_submit">
    <BUY_SELL>1</BUY_SELL>
    <COMMODITY_ID>17106082</COMMODITY_ID>
    <PRICE>5400.0</PRICE>
    <QTY>1</QTY>
    <S_I>527178095144368734</S_I>
    <U>1001000208</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REP name="order_submit">
    <RESULT>
      <RETCODE>-1611</RETCODE>
      <MESSAGE>???ڲ??ǽ???ʱ?䣡</MESSAGE>
    </RESULT>
  </REP>
</MEBS_MOBILE>
```


### <a id="issue_order">申购</a>

- 字段
	- C_I, 代码
	- S_I, 登录的retcode
	- I_QTY, 购买数量
	- U, 账号ID

	
### <a id="marketlogout">退出市场登录</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="marketlogout">
    <MARKETID>70</MARKETID>
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>527379524440299285</SESSIONID>
    <TRADERID>1001000208</TRADERID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="marketlogout">
    <result>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```

### <a id="user_logoff">用户登出</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="user_logoff">
    <S_I>527178095144368734</S_I>
    <U>1001000208</U>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs_mobile>
  <rep name="user_logoff">
    <result>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs_mobile>
```


### <a id="issue_commodity_detail">申购信息详情</a>

- 请求
	- C_I: 代码
	- S_I: Session/登录的retcode
	- U: 用户账号


- 返回
	- RESULT
	  	- CH_A: 申购最小变动数量
    	- CO_I: 商品代码
  		- CO_N: 商品名
  		- E_D: 结束时间 YYYY-mm-dd
  		- MAX_A: 最大申购量
  		- MAX_CA: 总库存
  		- MIN_A: 最小申购量
  		- MESSAGE: ??
  		- PRC: 申购价格
  		- QTY: 申购数量
  		- RETCODE:
  		- S_D: 开始时间 YYYY-mm-dd
  		- TTLREC: 总数量

  		
### <a id="order_cancel">撤销委托</a>

- 请求
	- ORDER_NO: 订单号
	- S_I: Session/登录的retcode
	- U: 账号

### <a id="issue_trade_query">申购中签查询</a>

- 请求
	- E_D: 结束时间
	- S_D: 开始时间
	- S_I: Session/登录的retcode
	- U: 账号

- 返回
	- RESULT
		- MESSAGE
		- RETCODE
		- TTLREC
	- RESULTLIST
		- REC
			- B_D: 中签时间 YYYY-mm-dd
			- CO_I: 代码
			- CO_N: 品名
			- IC: 成交金额
			- ICF: 发行服务费
			- OR_N: 订单号
			- PRI: 中签价格+服务费
			- QTY: 中签数量
			- SE_F: 发行分类(1=定价摇号)
			- TI: 结果时间: YYYY-mm-dd HH:MM:SS
			- TR_N: 交易号
			
### <a id="quotationserverinfo">行情服务器查询</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="quotationserverinfo">
    <PINSCODE>jingchao146810398069841090</PINSCODE>
    <SESSIONID>617437261711558182</SESSIONID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS>
  <REP name="quotationserverinfo">
    <RESULTLIST>
      <REC>
        <IP>118.145.4.148</IP>
        <NAME>??ͨ</NAME>
        <SOCKETPORT>40600</SOCKETPORT>
        <HTTPPORT>40700</HTTPPORT>
      </REC>
      <REC>
        <IP>115.182.221.26</IP>
        <NAME>????</NAME>
        <SOCKETPORT>40600</SOCKETPORT>
        <HTTPPORT>40700</HTTPPORT>
      </REC>
    </RESULTLIST>
    <RESULT>
      <RETCODE>0</RETCODE>
      <MESSAGE/>
    </RESULT>
  </REP>
</MEBS>
```


### <a id="getcustominfo">获取用户信息</a>

- 请求

```xml
<?xml version='1.0' encoding='GBK'?>
<MEBS_MOBILE>
  <REQ name="getcustominfo">
    <FRAMEID>-1</FRAMEID>
    <SESSIONID>617437261711558182</SESSIONID>
    <USERID>jingchao</USERID>
  </REQ>
</MEBS_MOBILE>
```

- 返回

```html
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<mebs>
  <rep name="getcustominfo">
    <result>
      <sty>0</sty>
      <ref>2</ref>
      <mars>16,15,53,19,77,36,30,42,33,56,78,79,75,80,81,31,32,34,83,84,37,85,40,87,88,89,41,90,91,92,43,93,94,44,95,45
,46,97,47,48,49,98,14,13,99,12,51,52,11,17,20,21,54,22,27,60,23,55,57,29,26,25,35,24,61,58,39,86,38,62,63,64</mars>
      <updatetime>2015-08-06 16:36:51</updatetime>
      <retcode>0</retcode>
      <message/>
    </result>
  </rep>
</mebs>
```