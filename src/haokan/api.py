from flask import Blueprint, request
from flask.views import MethodView
from models import Profile
import json


app=Blueprint("haokan", __name__)

@app.route("/")
def index():
    return "ok"

class DumpProfile(MethodView):

    def post(self):
        res={}
        info = self.get_info()
        res['url'] = self.get_url()
        res.update(info)
        res['form'] = json.dumps(request.form) if request.form else None
        res['headers'] = dict(request.headers)
        res['headers']["Host"]="sv.baidu.com"
        res["headers"] = json.dumps(res["headers"])
        profile = Profile.query.filter_by(uid=info["uid"]).first()
        if profile:
            profile.update(**res)
        else:
            profile = Profile()
            profile.create(**res)
        return "ok"

    def get_url(self):
        path, args = request.full_path.split("?")
        temp=[]
        for pair in args.split("&"):
            k, v = pair.split("=")
            if k!="info":temp.append(k+"="+v)
        return path+"?"+"&".join(temp)

    def get_info(self):
        infostr = request.args.get("info", "{}")
        info = json.loads(infostr)
        res={}
        fields = {"displayname", "username", "email", "phone", "app", "uid"}
        for f in fields:
            res[f] = info[f]
        return res

app.add_url_rule("/dump", view_func=DumpProfile.as_view("dump"))
