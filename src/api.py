from flask import Blueprint, request
import json

app=Blueprint("api", __name__)

@app.route("/haokan/api", methods=["GET", "POST"])
def test():
    res={}
    res['url'] = request.full_path
    res['form'] = dict(request.form)
    res['headers'] = dict(request.headers)
    res['headers']["Host"]="sv.baidu.com"
    with open("here.json", "w") as outf:
        json.dump(res, outf)
    return "ok"
