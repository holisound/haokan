# -*- coding: utf-8 -*-
import platform
import xml.etree.ElementTree as ET
from os import path

from flask import request, flash, render_template, url_for, abort, current_app
import config
import base64
from datetime import datetime, timedelta
import json
from bs4 import BeautifulSoup
from functools import wraps
from sqlalchemy.ext.declarative import DeclarativeMeta
from math import ceil


def to_dict(data):
    jsonstr = json.dumps(data, cls=AlchemyEncoder,
                         check_circular=False, skipkeys=True)
    ret = json.loads(jsonstr)
    return ret

def init_app(app):
    def static_url(fn):
        filepath = path.join(app.static_folder, fn)
        if platform.system() == 'Windows':
            filepath = filepath.replace('/', '\\')
        v = path.getmtime(filepath)
        return url_for('static', filename=fn, v=int(v))

    @app.context_processor
    def ctx_pr():
        return {
            'static_url': static_url,
        }


def args_get(key, default=None, type=None, required=False):
    val = request.args.get(key, default)
    if not val:
        if required:
            raise Exception('Missing query argument %r' % key)
        return default
    if type is not None:
        val = type(val)
    return val


def form_get(key, default=None, type=None, required=False):
    val = request.form.get(key, default)
    if not val:
        if required:
            raise Exception('Missing form argument %r' % key)
        return default
    if type is not None:
        val = type(val)
    return val


def get_subelements(ele, tagname, only_one=True):
    ret = []
    for sub in ele:
        if tagname == sub.tag:
            if only_one:
                return sub
            ret.append(sub)
    return ret

def excludes(keys=(), values=()):
    def _decorator(f):
        def _func(params):
            _the_params = {
                k: v for (k, v) in params.items()
                if (k not in keys) and (v not in values)}
            return f(_the_params)

        return _func

    return _decorator

def groupby2(iterObj, key):
    _dict = {}
    for i in iterObj:
        k = key(i)
        _dict.setdefault(k, [])
        _dict[k].append(i)
    return _dict.iteritems()

class StringCooker(object):
    @staticmethod
    def _translate(s, encoded):
        from string import maketrans   # 引用 maketrans 函数。
        intab = "AbdGhjm1pt9Z="
        outtab = "192AGZbdhjmpt"
        if encoded:
            trantab = maketrans(intab, outtab)
        else:
            trantab = maketrans(outtab, intab)
        return s.translate(trantab);
    
    def encode(self, s):
        encoded = base64.b64encode(s)
        return self._translate(encoded, True)
        
    def decode(self, s):
        encoded = self._translate(s, False)
        return base64.b64decode(encoded)

string_cooker = StringCooker()

def date_from_to(start, end, input_fmt='%Y-%m-%d', output_fmt='%Y-%m-%d'):
    '''
    start: '2017-08-25'
    end : '2017-08-31'
    ret: ['2017-08-25', '2017-08-26',...,'2017-08-31']
    '''
    startDate = datetime.strptime(start, input_fmt)
    endDate = datetime.strptime(end, input_fmt)
    n = 1
    ret = [startDate]
    while ret[-1] < endDate:
        ret.append(startDate + timedelta(days=n))
        n += 1
    ret = [r.strftime(output_fmt) for r in ret]
    return ret

def print_json(data):
    print json.dumps(data, indent=True)

def fill_null_flat(data, endpos=None):
    """
    endpos:
      not include `null` to the right of endpos
    """
    to_fill = None
    for idx, val in enumerate(data):
        if endpos and idx > endpos:
            break
        if val is None:
            if to_fill is not None:
                data[idx] = to_fill
        else:
            to_fill = val
    return data

def fill_null_linear(data):
    # [0, null, null ,null , 8 ...] => [0, 2, 4, 6, 8, ...]
    def get_arr(a, b, lng):
        step = float(b - a) / (lng - 1)
        ret = [a]
        while len(ret) < lng - 1:
            ret.append(ret[-1] + step)
        ret += [b]
        return [round(i, 1) for i in ret]
    ret = []
    remains = data
    a = None
    b = None
    curpos = 0
    startpos = None
    while len(remains) > curpos:
        b = remains[curpos]
        if b is not None:
            if a is not None:
                if len(remains) - curpos == 1:
                    ret += get_arr(a, b, (curpos - startpos + 1))
                else:
                    ret += get_arr(a, b, (curpos - startpos + 1))[:-1]
                remains = remains[curpos - 1:]
                curpos = 0
                a = None
            else:
                startpos = curpos
                a = b
        curpos += 1
    return ret

def token_required(access_token):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            with current_app.app_context():
                token = args_get("token")
                if token != current_app.config[access_token]:
                    abort(403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__

class ModelMixin(object):
    def to_dict(self):
        tablename = self.__tablename__
        table = self.metadata.tables[tablename]
        ret = {}
        for key in table.columns.keys():
            ret[key] = getattr(self, key)
        return ret

    @classmethod
    def get_model_columns(cls):
        model_inst = cls()
        tablename = model_inst.__tablename__
        table = model_inst.metadata.tables[tablename]
        return table.columns.keys()


class Pagination(object):

    def __init__(self, page, per_page, objects):
        self.page = page
        self.per_page = per_page
        self.objects = objects
        self.total_count = len(objects)

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and \
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num

    def get_page_objects(self, page):
        page_objects = self.objects[self.per_page * (page - 1): self.per_page * page]
        return page_objects

def kv_to_vk(dictObj):
    return {v: k for k, v in dictObj.items()}

class SerialList(list):
    """
    taken elements of string type only
    numbered element, if given element duplicated
    """
    def append(self, e, serial_format="%s-%d"):
        if not isinstance(e, (str, unicode)):
            raise TypeError("[string] type only!")
        if e in self:
            start = 1
            seed = e
            while e in self:
                e = serial_format % (seed, start)
                start += 1
        super(SerialList, self).append(e)

def main():
    sample = [0.0, None, None, None, None, None, None, 6.0, None, None, None, None, None, None, 12.0, None, None, None, None, None, None, 17.0, None, None, None, None, None, None, 28.6, None, None, None, None, None, None, 40.2, None, None, None, None, None, None, 40.2, None, None, None, None, None, None, 40.2, None, None, None, None, None, None, 51.8, None, None, None, None, None, None, 63.4, None, None, None, None, None, None, 75.0, None, None, None, None, None, None, 82.9, None, None, None, None, None, None, 91.2, None, None, None, None, None, None, 99.7, None, None, None, None, None, None, 100.0]
    print len(sample)
    ret= fill_null_linear(sample)
    # ret = fill_null_flat(sample)
    print len(ret)
    print ret
    # print parse_output('./outputs/project 1/1/log-20170313-111655.html')
    # cooker = StringCooker()
    # s = 'thinkcloud'
    # assert cooker.decode(cooker.encode(s)) == s
    # print  date_from_to('2017-08-25', '2017-08-31', '%Y-%m-%d', '%Y/%m/%d')
    #print parse_redfish_output(r'C:\Users\wangwh8\workspace\redfish-ci\logs\ConformanceHtmlLog_11_14_2017_171247.html')
    # print parse_uefi_validation_index('/srv/project/standalone-page/outputs/uefi_validation/20/lnvgy_fw_uefi_iver15f-1.02_anyos_32-64/index.html')
if __name__ == '__main__':
    main()
