from flask import Blueprint, request
from models import Profile
import json


app=Blueprint("haokan", __name__)


@app.route("", methods=["GET", "POST"])
def dump_profile():
    res={}
    res['url'] = request.full_path
    res["phone"] = request.args.get("phone")
    res['form'] = json.dumps(request.form) if request.form else None
    res['headers'] = dict(request.headers)
    res['headers']["Host"]="sv.baidu.com"
    res["headers"] = json.dumps(res["headers"])
    profile = Profile()
    profile.create(**res)
    return "ok"
