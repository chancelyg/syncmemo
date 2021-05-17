from flask import Flask, request, render_template, redirect, url_for, jsonify, g
from .utils import build_verify_code, api_response
from configparser import ConfigParser
from logging import config
from logging.handlers import RotatingFileHandler
import sys
import os
import yaml
import logging

# 读取当前运行目录绝对路径
root_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Logger config
if not os.path.exists('%s/logs' % root_path):
    os.mkdir('%s/logs' % root_path)
handler = RotatingFileHandler("logs/app.log", maxBytes=1024000, backupCount=10)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(threadName)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)

app.logger.info('启动程序')

configparser = ConfigParser()
if os.path.exists('%s/conf/app.conf' % root_path) is False:
    app.logger.error("配置文件app.conf不存在！请检查配置文件")
    sys.exit()
configparser.read('%s/conf/app.conf' % root_path, encoding='utf-8')
app.logger.info('配置文读取成功')

if not os.path.exists('%s/memo' % root_path):
    os.mkdir('%s/memo' % root_path)
    app.logger.info('便签存放目录已创建')


@app.route('/', methods=['GET'])
def index():
    verify_code = build_verify_code(length=int(configparser['general']['MEMO_ID_LENGTH']), just_uppercase=True)
    while True:
        if os.path.exists('%s/memo/%s.json' % (root_path, verify_code)):
            verify_code = build_verify_code(length=(configparser['general']['MEMO_ID_LENGTH']), just_uppercase=True)
            continue
        return render_template('template_index.html', verify_code=verify_code)


@app.route('/<memo_id>', methods=['GET'])
def memo_id(memo_id: str):
    if memo_id == 'help':
        return render_template('template_help.html')
    memo_path = os.path.join('%s/memo/' % root_path, memo_id.upper() + '.html')
    if not os.path.exists(memo_path):
            init_str = '<blockquote><p><font size="2" style="color: rgb(139, 170, 74);">便签ID -&nbsp;</font><b style=""><font size="3" style="" color="#c24f4a">%s</font></b></p><p><font size="2" color="#8baa4a">在另外一个设备访问本网站，输入相同的便签ID即可查看/编辑同一个便签内容</font></p></blockquote><hr/><p><br/></p>' % memo_id.upper()
            with open(memo_path, 'w', encoding='utf8') as f:
                f.write(init_str)
            app.logger.info('%s便签创建' % memo_path)
    with open(memo_path, 'r', encoding='utf8') as f:
        return render_template('template_memo.html', memo_id=memo_id, localStoreLength=configparser['general']['LOCAL_STORE_LENGTH'],span_time=configparser['general']['SAVE_SPANTIME'],memo_content=f.read())


@app.route('/rest/api/v1/memo', methods=['POST'])
def memo():
    if request.method == 'GET':
        if not request.args.get('memoID'):
            return api_response(success=False, message='参数不正确')
        memo_path = os.path.join('%s/memo/' % root_path, request.args.get('memoID').upper() + '.html')
        if not os.path.exists(memo_path):
            init_str = '<blockquote><p><font size="2" style="color: rgb(139, 170, 74);">便签ID -&nbsp;</font><b style=""><font size="3" style="" color="#c24f4a">%s</font></b></p><p><font size="2" color="#8baa4a">在另外一个设备访问本网站，输入相同的便签ID即可查看/编辑同一个便签内容</font></p></blockquote><hr/><p><br/></p>' % request.args.get(
                'memoID').upper()
            with open(memo_path, 'w', encoding='utf8') as f:
                f.write(init_str)
            app.logger.info('%s便签创建' % memo_path)
            return api_response(success=True, message='新建Memo成功', data=init_str)
        with open(memo_path, 'r', encoding='utf8') as f:
            return api_response(success=True, data=f.read(), message='获取成功')
    if request.method == 'POST':
        content = request.json.get('content')
        size = len(content) / 1024 / 1024
        if size > int(configparser['general']['MEMO_MAX_SIZE']):
            app.logger.warn('%s便签大小超过限制(%dMb)' % (request.json.get('memoID').upper(), size))
            return api_response(success=False, message='便签内容大小不能超过%sMb，保存失败' % configparser['general']['MEMO_MAX_SIZE'])
        memo_path = os.path.join('%s/memo/' % root_path, request.json.get('memoID').upper() + '.html')
        with open(memo_path, 'w', encoding='utf8') as f:
            f.write(content)
        app.logger.info('%s便签保存成功，文件大小%dKb' % (request.json.get('memoID').upper(), len(content) / 1024))
        return api_response(success=True, message='保存成功')