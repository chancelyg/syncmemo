import argparse

parser = argparse.ArgumentParser(description='Test for argparse')
parser.add_argument('--port', '-p', help='程序端口，默认8220', default='8220')
parser.add_argument('--host', '--host', help='程序Host,默认127.0.0.1', default='127.0.0.1')
args = parser.parse_args()

from flaskr import app

if __name__ == '__main__':
    app.run(host=args.host,port=int(args.port))