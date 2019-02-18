# -*- coding: utf-8 -*-
import requests
import urlparse
import time
import os
import sys
import argparse
import random
import glob

from analyze import Analyzer, JSONAnalyzer

reload(sys)

sys.setdefaultencoding('utf8')

curdir = os.path.dirname(__file__)




class Haokan(requests.Session):
    endpoint="https://sv.baidu.com"
    cond_vid=set()
    def __init__(self, params):
        super(Haokan, self).__init__()
        self.params=params

    def post_hongbao(self, data):

        self.params["cmd"]="haokan/hongbao"
        resp=self.post("/haokan/api",data=data)
        jd=resp.json()["haokan/hongbao"]["data"]
        if "errormsg" in jd: return "limit"
	return jd.get("tips", "")

    def _feed_data(self):
        self.params["cmd"]="feed"
        data={"feed":'method=get&rn=8&tag=recommend&sessionid=1546668632815&sid_debug=1732_2&refreshtype=0&refreshcount=2&card={"refresh_count":8,"card_last_showtime":1546137162451,"card_show_times":2}&adparam={"ac":"1","ver":"4.9.1.10","mod":"STF-AL00","ov":"8.0.0","imei":"0","cuid":"DF63276DF1BF8AE39A970FFE751BEA25|065051730766768","fmt":"json","apna":"com.baidu.haokan","eid":"1373_2,1436_1,1497_2,1580_1,1629_1,1647_1,1646_2,1708_1,1715_2,1716_2,1723_1,1738_1,1772_2,1776_1,1780_3,1781_1,1786_1,1796_1,1798_2,1800_2,1801_1,1804_1,1805_2,1806_4,1814_2","ot":"2","ct":"2","nt":"1","network":"1","android_id":"df93dd8cdb542063","ua":"1080_1920_android_4.9.1.10_480","install_timestamp":"1545483021","iad":331,"from":"1015351b","cfrom":"1014517k","videomute":"0","apinfo":"0","latitude":"","longitude":"","pid":"1510566610070","tabn":"推荐","tabid":"recommend","ext":"[{\"k\":\"user_source\",\"v\":\"1015351b\"}]","flr":"-1","fc":"8","ft":"4","is_https":"1","pre_feed_count":3,"feed_total":5}&gr_param=[{"id":"8593551504666944757","show":0,"clk":0,"show_ts":0,"clk_ts":0},{"id":"3359395390840942425","show":0,"clk":0,"show_ts":0,"clk_ts":0},{"id":"1451023015369360190","show":1,"clk":0,"show_ts":1546668648272,"clk_ts":0},{"id":"14966060665065951080","show":1,"clk":0,"show_ts":1546668648252,"clk_ts":0}]&shuaxin_id=1546669267643'}
        resp=self.post('/haokan/api', data=data)
        return resp.json()

    def get_video_id(self):
        if not self.cond_vid:
            feeddata=self._feed_data()
            for each in feeddata["feed"]["data"]["list"]:
                if each["content"].get("duration",0) > 60:
                    self.cond_vid.add(each["content"]["vid"])
        return self.cond_vid.pop()

    def _concat_url(self, url):
        return urlparse.urljoin(self.endpoint, url)

    def post(self, url, *args, **kwargs):
        return super(Haokan, self).post(self._concat_url(url), *args, **kwargs)


def checkin(headers, productid):
    resp = requests.post("https://haokan.baidu.com/activity/acusercheckin/update?productid=%s" % productid, data={"productid":productid}, headers=headers)
    jd= resp.json()
    return jd

def bindinvitecode(headers, productid, invitecode):
    resp = requests.post("https://haokan.baidu.com/activity/tasks/bindinvitecode?productid=%s&inviteCode=%s"%(productid, invitecode) , 
        data={"productid": productid, "inviteCode": invitecode}, headers=headers)
    print resp.content

def get_filepaths(args):
    if args.file:
        fp = os.path.join(curdir, args.file)
        if not os.path.isfile(fp):
            print(">>>[error] File not exits!!!")
            exit(0)
        return [fp]
    if args.dir:
        return glob.glob(os.path.join(curdir, args.dir, "*.*"))

    assert 0, "should not be here!!!"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog="runner.py",
        version='v0.1',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="automation script")
    # common
    parser.add_argument("-f", "--profile", dest="file", action="store",
                        help="filepath of the profile choosed")
    parser.add_argument("-p", "--productid", dest="productid", default=1, type=int,
        choices=[1,2,6],action="store")
    # register parsers
    subparsers = parser.add_subparsers(help="commands", dest="command")
    # hongbao
    hongbao = subparsers.add_parser("hongbao", help="hongbao")
    hongbao.add_argument("-d", "--dir", dest="dir", action="store", help="directory of profiles")
    hongbao.add_argument("-l", "--limit", dest="limit", default=30, type=int, action="store")
    hongbao.add_argument("--no-checkin", dest="nocheckin", action="store_true")
    # bind
    bind = subparsers.add_parser("bind", help="bind invitecode")
    bind.add_argument("-b", "--bind-invitecode", dest="invitecode", action="store")

    args = parser.parse_args()
    productid = args.productid

    if args.command == "hongbao":
        limit = args.limit
        while 1:
            filepaths = get_filepaths(args)
            random.shuffle(filepaths)
            a = time.time()
            tip_empty = 0
            for fp in filepaths:
                print '--->SOURCE: %s' % fp
                if fp.endswith(".txt"):
                    anaz=Analyzer(fp)
                elif fp.endswith(".json"):
                    anaz=JSONAnalyzer(fp)
                else:exit(0)
                clt=Haokan(anaz.get_params())
                clt.headers=anaz.get_headers()
                if not args.nocheckin:
                    print '--->CHECKIN', checkin(anaz.get_headers(), productid)
                count=0
                while count < limit:
                    postdata=anaz.get_hongbao_post_data(clt.get_video_id(), productid)
                    tips=clt.post_hongbao(postdata)
                    if tips=="limit": break
                    if tips=="":
                        tip_empty+=1
                        if tip_empty >= 2: break
                    count+=1
                    print count, "[hongbao] %s TIPS:%s"% (time.asctime(), tips)
                    if count < limit:
                        waitsec=60 + 60*random.random()
                        time.sleep(waitsec)
                print "--->Up to Limit, Exit Loop."
            b = time.time()
            intervals = 3600*24-int(b-a)+random.randint(-600, 600 )
            time.sleep(intervals)
    elif args.command == "bind":
        fp = get_filepaths(args)[0]
        print '--->SOURCE: %s' % fp
        if fp.endswith(".txt"):
            anaz=Analyzer(fp)
        elif fp.endswith(".json"):
            anaz=JSONAnalyzer(fp)
        else:exit(0)
        bindinvitecode(anaz.get_headers(), productid, args.invitecode)


