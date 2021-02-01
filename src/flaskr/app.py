from flask import Flask, request, render_template, redirect, url_for, jsonify
from .utils import build_verify_code, api_response
from configparser import ConfigParser
from logging import config
import sys
import os
import yaml
import logging

# 读取当前运行目录绝对路径
current_path = os.path.dirname(os.path.abspath(__file__))

# 日志配置
if not os.path.exists('logs'):
    os.mkdir('logs')
with open('%s/logging.yaml' % current_path, 'r', encoding='utf-8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
    logging.config.dictConfig(config)
main_logger = logging.getLogger('main.common')

main_logger.info('启动程序')
app = Flask(__name__)

app_config_path = '%s/conf/app.conf' % current_path

main_logger.info('配置文件路径->%s' % app_config_path)
configparser = ConfigParser()
if os.path.exists(app_config_path) is False:
    main_logger.error("配置文件%s不存在！请检查配置文件" % app_config_path)
    sys.exit()
configparser.read(app_config_path, encoding='utf-8')
main_logger.info('配置文读取成功')


@app.route('/', methods=['GET', 'POST'])
@app.route('/<memo_id>', methods=['GET', 'POST'])
def index(memo_id=None):
    if not memo_id:
        verify_code = build_verify_code(length=5, just_uppercase=True)
        while True:
            if os.path.exists('./tmp/%s.json' % verify_code):
                verify_code = build_verify_code(length=5, just_uppercase=True)
                continue
            break
        main_logger.info('%s便签创建' % verify_code)
        return redirect(url_for('index', memo_id=verify_code))
    main_logger.info('%s便签请求访问，请求方式%s' % (memo_id, request.method))
    memo_path = 'tmp/%s.html' % memo_id
    if request.method == 'GET':
        if os.path.exists(memo_path):
            with open(memo_path, 'r', encoding='utf8') as f:
                return render_template('index.html', memo_content=f.read(),span_time=configparser['general']['SAVE_SPANTIME'])
        return render_template('index.html',span_time=configparser['general']['SAVE_SPANTIME'])
    if request.method == 'POST':
        content = request.json.get('content')
        size = len(content) / 1024 / 1024
        if size > int(configparser['general']['MEMO_MAX_SIZE']):
            main_logger.warn('%s便签大小超过限制(%dMb)' % (memo_id, size))
            return api_response(success=False, message='便签内容大小不能超过5Mb，保存失败')
        if not os.path.exists('tmp'):
            os.mkdir('tmp')
        with open(memo_path, 'w', encoding='utf8') as f:
            f.write(content)
        main_logger.info('%s便签保存成功，文件大小%dKb' % (memo_id, len(content) / 1024))
        return api_response(success=True, message='保存成功')
