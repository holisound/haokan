# coding:utf-8

import os
import urllib
import json


curdir = os.path.dirname(__file__)


class JSONAnalyzer(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self._load(filepath)

    def _load(self, filepath):
        with open(filepath) as inf:
            self.data = json.load(inf)

    def get_params(self):
        _, querystring = self.data['url'].split('?')
        res = {}
        for pair in querystring.split('&'):
            k, v = pair.split('=')
            res[k] = v
        return res

    def get_hongbao_post_data(self, videoid, productid):
        text = self.data['form']["haokan/hongbao"]
        arr = []
        for frag in text.split('&'):
            k, v = frag.split('=')
            if k == "videoid":
                v = str(videoid)
            elif k == "productid":
                v = str(productid)
            arr.append(k + '=' + v)
        return {"haokan/hongbao": '&'.join(arr)}

    def get_headers(self):
        return self.data['headers']


class Analyzer(object):

    def __init__(self, filepath):
        self.filepath = filepath
        self._load(filepath)

    def _load(self, filepath):
        with open(filepath) as inf:
            content = inf.read()
        self.lines = [line for line in content.replace('\r', '').split('\n') if line.strip()]

    def get_params(self):
        querystring = self.lines[0].split('?')[1].split()[0]
        res = {}
        for pair in querystring.split('&'):
            k, v = pair.split('=')
            res[k] = v
        return res

    def get_hongbao_post_data(self, videoid, productid):
        tline = ''
        for line in self.lines:
            if urllib.unquote(line).startswith("haokan/hongbao="):
                tline = line
        text = urllib.unquote(tline).split('=', 1)[1]
        arr = []
        for frag in text.split('&'):
            k, v = frag.split('=')
            if k == "videoid":
                v = str(videoid)
            elif k == "productid":
                v = str(productid)
            arr.append(k + '=' + v)
        return {"haokan/hongbao": '&'.join(arr)}

    def get_headers(self):
        fields = {

            "Charset",
            "XRAY-TRACEID",
            "XRAY-REQ-FUNC-ST-DNS",
            "Host",
            "Connection",
            "Content-Length",
            "User-Agent",
            "Cookie",
            "Accept-Language",
            "Content-Type",
            "Accept",
            "X-TurboNet-Info",
            "Accept-Encoding",
        }

        header_lines = []
        flag = False
        for line in self.lines[1:]:
            if ':' not in line:
                continue
            if line.split(':')[0].strip() in fields:
                header_lines.append(line)
            else:
                break
        res = {}
        for line in header_lines:
            k, v = line.split(':', 1)
            res[k.strip()] = v.strip()
        return res


if __name__ == '__main__':
    ana = Analyzer("dump.txt")
    # print ana.get_params()
    # print ana.get_headers()

