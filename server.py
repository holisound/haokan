from flask import Flask, request
import json

app=Flask(__name__)

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


app.run(debug=True, host="0.0.0.0", threaded=True)


