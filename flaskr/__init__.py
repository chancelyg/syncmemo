from flask import Flask, g, request, render_template
from flask_compress import Compress
from flaskr.dependents import config, CONST_VERSION, Memo,logger
from flaskr.utils import build_random_string, json_response, build_content_qrcode
import base64


app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
Compress(app)

# Memo initialization
memo = Memo(disk_cache_dir=config["system"]["cache"], expire=config["memo"]["expire"])


@app.route("/", methods=["GET"])
def index():
    verify_code = build_random_string(length=int(config["memo"]["id_defalt_length"]))
    logger.info(f"build memo id {verify_code}.")
    while True:
        if not memo.get(verify_code):
            break
        verify_code = build_random_string(length=(config["memo"]["id_defalt_length"]))
        logger.warning(f"build new memo id {verify_code}.")
    return render_template("template_index.html", verify_code=verify_code)


@app.route("/<memo_id>", methods=["GET"])
def get_memo(memo_id: str):
    if memo_id == "help":
        return render_template("template_help.html", max_size=config["memo"]["max_size"], expire=config["memo"]["expire"], version=CONST_VERSION)
    qrcode_base64 = "data:image/png;base64,%s" % build_content_qrcode(content=request.base_url)
    base64_string = base64.b16encode(memo_id.encode()).decode()
    logger.info(f"convert memo id {memo_id} to base64 string {base64_string}.")
    return render_template("template_memo.html", memo_id=memo_id, localStoreLength=10, img=qrcode_base64, memo_content=memo.get(memo_id.upper()), base64_string=base64_string)


@app.route("/immutable/<base64_string>", methods=["GET"])
def get_immutable(base64_string: str):
    logger.info(f"visit base64 string {base64_string}.")
    memo_id = None
    try:
        memo_id = base64.b16decode(base64_string.encode()).decode("utf8")
    except Exception:
        logger.exception(f"convert base64 string {base64_string} exception.")
        return render_template("template_404.html")
    if not memo.get(memo_id.upper()):
        return render_template("template_404.html")
    logger.info(f"convert the base64 string {base64_string} to the memo id {memo_id}.")
    return render_template("template_immutable.html", html=memo.get(memo_id.upper()))


@app.route("/rest/api/v1/memo", methods=["POST"])
def post_memo():
    max_size = config["memo"]["max_size"]
    memo_id = request.json.get("memoID").upper()
    content = request.json.get("content")
    size = len(content) / 1024 / 1024
    if size > int(max_size):
        logger.info(f"the memo id {memo_id} size {size} exceed max size {max_size}.")
        return json_response(success=False, message="the memo id {memo_id} size {size} exceed max size {max_size}.")
    logger.info(f"the memo id {memo_id} was saved successfully.")
    memo.set(key=memo_id, value=content)
    return json_response(success=True, message="the memo id {memo_id} was saved successfully.")


@app.before_request
def before_request():
    g.site = config["site"]
