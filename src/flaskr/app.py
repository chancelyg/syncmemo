from types import MethodType
from flask import Flask, g, jsonify, request, render_template
from .utils import BuildRandomString, APIResponse, BuildContentQRCode
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler
from flask_caching import Cache
from flask_compress import Compress
import sys
import os
import logging
import argparse
import base64

CONST_VERSION = 'V1.2.3'
CONST_ARGS_CACHE_NAME = 'CONST_ARGS_CACHE_NAME'

parser = argparse.ArgumentParser(description='Syncmemo for argparse')
parser.add_argument('--config', '-c', help='config path', default='config.ini')
args = parser.parse_args()

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
Compress(app)

configparser = ConfigParser()
if not os.path.exists(args.config):
    print("Error: config file not found!" % args.config)
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

app.logger.info('Read config file success')


def Run(self):
    self.run(host=configparser['general']['HOST'], port=int(configparser['general']['PORT']))
    self.debug = configparser['general']['debug'] == '1'


app.Run = MethodType(Run, app)

if not os.path.exists(os.path.dirname(configparser['store']['PATH'])):
    app.logger.info('Cache folder(%s) created' % os.path.dirname(configparser['store']['PATH']))
    os.makedirs(os.path.dirname(configparser['store']['PATH']))
app_cache = Cache(config={'CACHE_TYPE': 'filesystem', "CACHE_DEFAULT_TIMEOUT": 10, 'CACHE_DIR': configparser['store']['PATH']})
app_cache.init_app(app)
app.logger.info('Cache load success')

timeout = 60 * 60 * 24 * int(configparser['store']['TIMEOUT_DAY'])

app.logger.info('Memo valid %s days' % configparser['store']['TIMEOUT_DAY'])

old_version_memo_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')), 'memo')
if os.path.exists(old_version_memo_path):
    app.logger.info('Old version memo data found')
    for item in os.listdir(old_version_memo_path):
        try:
            file_name = os.path.splitext(os.path.split(item)[1])[0]
            file_path = os.path.join(old_version_memo_path, item)
            with open(file_path, 'r') as f:
                app_cache.set(file_name, f.read(), timeout=timeout)
            os.remove(file_path)
            app.logger.info('Update old version data to data cache, filename:%s' % file_name)
        except Exception:
            app.logger.exception('Read old version data exception')


@app.route('/', methods=['GET'])
def GetIndex():
    verify_code = BuildRandomString(length=int(configparser['memo']['MEMO_ID_LENGTH']))
    while True:
        if not app_cache.get(verify_code):
            break
        app.logger.debug('Memo(%s) found' % verify_code)
        verify_code = BuildRandomString(length=(configparser['memo']['MEMO_ID_LENGTH']))
    app.logger.info('Memo(%s) to be build' % verify_code)
    return render_template('template_index.html', verify_code=verify_code)


@app.route('/<memo_id>', methods=['GET'])
def GetMemo(memo_id: str):
    app.logger.info('Memo(%s) to be accessed' % memo_id)
    if memo_id == 'help':
        return render_template('template_help.html')
    if not app_cache.get(memo_id.upper()):
        app.logger.info('Memo(%s) to be created' % memo_id)
        app_cache.set(memo_id, '', timeout=timeout)
    qrcode_base64 = 'data:image/png;base64,%s' % BuildContentQRCode(content=request.base_url)
    hex_str = base64.b16encode(memo_id.encode()).decode()
    app.logger.info('Memo(%s) updated' % memo_id)
    return render_template('template_memo.html', memo_id=memo_id, localStoreLength=configparser['memo']['LOCAL_STORE_LENGTH'], span_time=configparser['memo']['SAVE_SPANTIME'], img=qrcode_base64, memo_content=app_cache.get(memo_id.upper()),hex_str=hex_str)


@app.route('/immutable/<hex_str>', methods=['GET'])
def GetImmutable(hex_str: str):
    app.logger.info('Memo(%s) show immutable page')
    memo_id = None
    try:
        memo_id = base64.b16decode(hex_str.encode()).decode('utf8')
    except Exception:
        return APIResponse(success=False, message='hex_str args illegal')
    if not app_cache.get(memo_id.upper()):
        return APIResponse(success=False, message='memo not found')
    return render_template('template_immutable.html', html=app_cache.get(memo_id.upper()))


@app.route('/rest/api/v1/memo', methods=['POST'])
def PostMemo():
    content = request.json.get('content')
    size = len(content) / 1024 / 1024
    if size > int(configparser['memo']['MEMO_MAX_SIZE']):
        app.logger.warning('Memo(%s) exceed max size(%smb)' % (request.json.get('memoID').upper(), size))
        return APIResponse(success=False, message='Memo exceed max size(%smb)' % configparser['memo']['MEMO_MAX_SIZE'])
    app_cache.set(request.json.get('memoID').upper(), content, timeout=timeout)
    app.logger.info('Memo(%s) save success, size is %s mb' % (request.json.get('memoID').upper(), len(content) / 1024))
    return APIResponse(success=True, message='save success')

@app.before_request
def BeforeRequest():
    g.site_name = configparser['general']['SITE_NAME']
    g.site_url = configparser['general']['SITE_URL']
    g.memo_max_size = configparser['memo']['MEMO_MAX_SIZE']
    g.timeout_day = configparser['store']['TIMEOUT_DAY']
    g.version = CONST_VERSION