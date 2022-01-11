from types import MethodType
from flask import Flask, request, render_template
from .utils import build_verify_code, api_response, build_qrcode
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler
from flask_caching import Cache
import sys
import os
import logging
import argparse

CONST_VERSION = 'V1.2.0'
CONST_ARGS_CACHE_NAME = 'CONST_ARGS_CACHE_NAME'

parser = argparse.ArgumentParser(description='Syncmemo for argparse')
parser.add_argument('--config', '-c', help='配置文件路径', default='config.ini')
args = parser.parse_args()

TIP_TEXT = '<blockquote> <p style="text-align:left;"> <font size="2">Hi，您可以随意编辑此便签内容（自动保存），通过以下2种途径可在其他设备直接访问修改后的便签</font> </p> <font size="2">1. 在其他设备访问本站（[url]）并输入便签ID </font> <font color="#c24f4a"><b> <font size="3">[memoid]</font> </b> </font> <font size="2">即可访问本便签</font> <p> <font size="2">2. 扫描以下二维码直接访问此便签</font> </p> <p><img src="[qrcode]" /><span style="font-size: 1em;"><br /></span></p> <p> <font size="2"> </font> </p> </blockquote> <hr /> <p><br /></p>'

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

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
            file_path = os.path.join(old_version_memo_path,item)
            with open(file_path,'r') as f:
                app_cache.set(file_name,f.read())
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
    if not app_cache.get(memo_id):
        init_str = '<blockquote><p><font size="2" style=""><font color="#4d80bf">Hi，您可以在另外一个设备访问本站，输入</font><font color="#c24f4a"> <b style=""> %s </b></font><font color="#4d80bf">即可查看或编辑同一个便签内容（编辑后在另外一个网页需刷新以便修改生效）</font></font></p></blockquote><hr/><p><br/></p>' % memo_id.upper(
        )
        qrcode_base64 = 'data:image/png;base64,%s' % build_qrcode(content=request.base_url)
        init_str = TIP_TEXT.replace('[url]', request.host_url)
        init_str = init_str.replace('[memoid]', memo_id)
        init_str = init_str.replace('[qrcode]', qrcode_base64)
        app_cache.set(memo_id, init_str, timeout=timeout)
    app.logger.info('便签（%s）已创建' % memo_id)
    return render_template('template_memo.html', memo_id=memo_id, localStoreLength=configparser['memo']['LOCAL_STORE_LENGTH'], span_time=configparser['memo']['SAVE_SPANTIME'], memo_content=app_cache.get(memo_id))


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
