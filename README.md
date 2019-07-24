# 金币兑换现金截图

<img src="https://github.com/holisound/haokan/blob/master/income.jpg?raw=true" width="300" height="500">

# 攻击思路
    1. 使用fiddler工具进行抓包，获得API地址和参数
    2. 抓取用户cookies保存为profile文件
    3. python基于requests开发CLI工具，绕过客户端进行请求攻击
    4. 将工具部署到服务器上，定时激活刷取金币
    5. 金币积累到一定数量后，人工进行提现
  
# 用法
```shell
$ python runner.py -h
usage: runner.py [-h] [-v] [-f FILE] [-p {1,2,6}] {hongbao,bind} ...

automation script

positional arguments:
  {hongbao,bind}        commands
    hongbao             hongbao
    bind                bind invitecode

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -f FILE, --profile FILE
                        filepath of the profile choosed (default: None)
  -p {1,2,6}, --productid {1,2,6}

$ python -u runner.py hongbao -d profiles/
--->SOURCE: profiles/yunfa.txt
--->CHECKIN {u'msg': u'\u7528\u6237\u5df2\u7b7e\u5230', u'errno': 10053, u'servertime': 1551152715, u'data': None, u'usedtime': u'0.035'}
1 [hongbao] Tue Feb 26 11:46:02 2019 TIPS:+10金币
2 [hongbao] Tue Feb 26 11:47:20 2019 TIPS:+10金币
3 [hongbao] Tue Feb 26 11:48:52 2019 TIPS:+10金币
4 [hongbao] Tue Feb 26 11:50:27 2019 TIPS:+10金币
5 [hongbao] Tue Feb 26 11:51:47 2019 TIPS:+10金币
... ...
26 [hongbao] Tue Feb 26 12:23:41 2019 TIPS:+10金币
27 [hongbao] Tue Feb 26 12:24:44 2019 TIPS:+10金币
28 [hongbao] Tue Feb 26 12:26:22 2019 TIPS:+10金币
29 [hongbao] Tue Feb 26 12:27:48 2019 TIPS:+10金币
30 [hongbao] Tue Feb 26 12:29:42 2019 TIPS:+10金币
--->Up to Limit, Exit Loop.
```
