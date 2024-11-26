from flask import Flask, g, request, render_template
from flask_compress import Compress
from flaskr.dependents import cache, config, CONST_VERSION
from flaskr.utils import build_random_string, json_response, build_content_qrcode
import base64


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
Compress(app)


@app.route("/", methods=["GET"])
def index():
    verify_code = build_random_string(length=int(config["memo"]["id_defalt_length"]))
    while True:
        if not cache.get(verify_code):
            break
        verify_code = build_random_string(length=(config["memo"]["id_defalt_length"]))
    return render_template("template_index.html", verify_code=verify_code)


@app.route("/<memo_id>", methods=["GET"])
def get_memo(memo_id: str):
    if memo_id == "help":
        return render_template("template_help.html", max_size=config["memo"]["max_size"], expire=config["memo"]["expire"], version=CONST_VERSION)
    if not cache.get(memo_id.upper()):
        if config["memo"]["expire"] == 0:
            cache.set(key=memo_id.upper(), value="")
        if config["memo"]["expire"] != 0:
            cache.set(key=memo_id.upper(), value="", expire=config["memo"]["expire"])

    qrcode_base64 = "data:image/png;base64,%s" % build_content_qrcode(content=request.base_url)
    hex_str = base64.b16encode(memo_id.encode()).decode()
    return render_template("template_memo.html", memo_id=memo_id, localStoreLength=10, img=qrcode_base64, memo_content=cache.get(memo_id.upper()), hex_str=hex_str)


@app.route("/immutable/<hex_str>", methods=["GET"])
def get_immutable(hex_str: str):
    memo_id = None
    try:
        memo_id = base64.b16decode(hex_str.encode()).decode("utf8")
    except Exception:
        return json_response(success=False, message="hex_str args illegal")
    if not cache.get(memo_id.upper()):
        return json_response(success=False, message="memo not found")
    return render_template("template_immutable.html", html=cache.get(memo_id.upper()))


@app.route("/rest/api/v1/memo", methods=["POST"])
def post_memo():
    memo_id = request.json.get("memoID").upper()
    content = request.json.get("content")
    size = len(content) / 1024 / 1024
    if size > int(config["memo"]["max_size"]):
        return json_response(success=False, message="Memo exceed max size(%smb)" % config["memo"]["max_size"])
    if config["memo"]["expire"] == 0:
        cache.set(key=memo_id, value=content)
    if config["memo"]["expire"] != 0:
        cache.set(key=memo_id, value=content, expire=config["memo"]["expire"])
    return json_response(success=True, message="save success")


@app.before_request
def before_request():
    g.site = config["site"]
