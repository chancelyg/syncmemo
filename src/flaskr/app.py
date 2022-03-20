from types import MethodType
from flask import Flask, g, jsonify, request, render_template
from .utils import build_verify_code, api_response, build_qrcode
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler
from flask_caching import Cache
from flask_compress import Compress
import sys
import os
import logging
import argparse

CONST_VERSION = 'V1.2.1'
CONST_ARGS_CACHE_NAME = 'CONST_ARGS_CACHE_NAME'

parser = argparse.ArgumentParser(description='Syncmemo for argparse')
parser.add_argument('--config', '-c', help='配置文件路径', default='config.ini')
args = parser.parse_args()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
Compress(app)

configparser = ConfigParser()
if not os.path.exists(args.config):
    print("配置文件%s不存在！请检查配置文件" % args.config)
    sys.exit()
configparser.read(args.config, encoding='utf-8')

# Logger config
if os.path.dirname(configparser['log']['PATH']) and not os.path.exists(os.path.dirname(configparser['log']['PATH'])):
    os.makedirs(os.path.dirname(configparser['log']['PATH']))
handler = RotatingFileHandler(configparser['log']['PATH'], maxBytes=1024000, backupCount=10)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(threadName)s - %(message)s')
handler.setFormatter(formatter)
app.logger.setLevel(configparser['log']['LEVEL'])
app.logger.addHandler(handler)

app.logger.info('读取配置文件成功->%s' % args.config)


def running(self):
    self.run(host=configparser['general']['HOST'], port=int(configparser['general']['PORT']))
    self.debug = configparser['general']['debug'] == '1'


app.running = MethodType(running, app)

if not os.path.exists(os.path.dirname(configparser['store']['PATH'])):
    app.logger.info('创建缓存目录->%s' % os.path.dirname(configparser['store']['PATH']))
    os.makedirs(os.path.dirname(configparser['store']['PATH']))
app_cache = Cache(config={'CACHE_TYPE': 'filesystem', "CACHE_DEFAULT_TIMEOUT": 10, 'CACHE_DIR': configparser['store']['PATH']})
app_cache.init_app(app)
app.logger.info('缓存读取成功')

timeout = 60 * 60 * 24 * int(configparser['store']['TIMEOUT_DAY'])

app.logger.info('便签默认有效期：%s天' % configparser['store']['TIMEOUT_DAY'])

old_version_memo_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')), 'memo')
if os.path.exists(old_version_memo_path):
    app.logger.info('检测到旧版本的MEMO便签文件%d个' % len(os.listdir(old_version_memo_path)))
    for item in os.listdir(old_version_memo_path):
        try:
            file_name = os.path.splitext(os.path.split(item)[1])[0]
            file_path = os.path.join(old_version_memo_path, item)
            with open(file_path, 'r') as f:
                app_cache.set(file_name, f.read(), timeout=timeout)
            os.remove(file_path)
            app.logger.info('%s已写入缓存中，文件已删除' % file_name)
        except Exception:
            app.logger.exception('%s便签读取异常！')


@app.route('/', methods=['GET'])
def index():
    verify_code = build_verify_code(length=int(configparser['memo']['MEMO_ID_LENGTH']), just_uppercase=True)
    app.logger.debug('验证码生成->%s' % verify_code)
    while True:
        if app_cache.get(verify_code):
            app.logger.debug('验证码%s已存在缓存中' % verify_code)
            verify_code = build_verify_code(length=(configparser['memo']['MEMO_ID_LENGTH']), just_uppercase=True)
            continue
        app.logger.info('便签（%s）分配成功' % verify_code)
        return render_template('template_index.html', verify_code=verify_code)


@app.route('/<memo_id>', methods=['GET'])
def memo_id(memo_id: str):
    if memo_id == 'help':
        app.logger.debug('HELP页面被读取')
        return render_template('template_help.html')
    if not app_cache.get(memo_id.upper()):
        app_cache.set(memo_id, '', timeout=timeout)
    qrcode_base64 = 'data:image/png;base64,%s' % build_qrcode(content=request.base_url)
    app.logger.info('便签（%s）已创建' % memo_id)
    return render_template('template_memo.html', memo_id=memo_id, localStoreLength=configparser['memo']['LOCAL_STORE_LENGTH'], span_time=configparser['memo']['SAVE_SPANTIME'], img=qrcode_base64, memo_content=app_cache.get(memo_id.upper()))


@app.route('/rest/api/v1/memo', methods=['POST'])
def memo():
    content = request.json.get('content')
    size = len(content) / 1024 / 1024
    if size > int(configparser['memo']['MEMO_MAX_SIZE']):
        app.logger.warning('便签（%s）大小超过限制（%dMb）' % (request.json.get('memoID').upper(), size))
        return api_response(success=False, message='便签内容大小不能超过%sMb，保存失败' % configparser['memo']['MEMO_MAX_SIZE'])
    app_cache.set(request.json.get('memoID').upper(), content, timeout=timeout)
    app.logger.info('便签（%s）保存成功，内容大小%dKb' % (request.json.get('memoID').upper(), len(content) / 1024))
    return api_response(success=True, message='保存成功')


@app.route('/manifest.webmanifest', methods=['GET'])
def manifest():
    manifest_dict = {}
    manifest_dict['start_url'] = '.'
    manifest_dict['prefer_related_applications'] = True
    manifest_dict['icons'] = [{"sizes": "192x192", "src": "/static/img/favicon.webp", "type": "image/webp"}, {"sizes": "512x512", "src": "/static/img/favicon.webp", "type": "image/webp"}]
    manifest_dict['name'] = configparser['general']['SITE_NAME']
    manifest_dict['short_name'] = configparser['general']['SITE_NAME']
    manifest_dict['theme_color'] = 'teal'
    manifest_dict['background_color'] = '#ffffff'
    manifest_dict['display'] = 'standalone'
    return jsonify(manifest_dict)


@app.route('/sw.js', methods=['GET'])
def swjs():
    return app.send_static_file('js/sw.js')


@app.before_request
def before_request():
    g.site_name = configparser['general']['SITE_NAME']
    g.site_url = configparser['general']['SITE_URL']
    g.memo_max_size = configparser['memo']['MEMO_MAX_SIZE']
    g.timeout_day = configparser['store']['TIMEOUT_DAY']
    g.version = CONST_VERSION