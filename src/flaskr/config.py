import os
from configparser import ConfigParser

configparser = ConfigParser()

def init_config_parser():
    if not os.environ.get('MEMO_CONF') or not os.path.exists(os.environ.get('MEMO_CONF')):
        print('ERROR: %s CONF NOT FOUND' % os.environ.get('MEMO_CONF'))
    configparser.read(os.environ.get('MEMO_CONF'), encoding='utf-8')