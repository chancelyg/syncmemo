服务Demo：[https://memo.chancel.ltd](https://memo.chancel.ltd)

# 1. SyncMemo

一个多设备同步文本/图片内容的开源便签Web服务

- 参考Demo（也可直接使用）：[https://memo.chancel.ltd](https://memo.chancel.ltd)

如何使用？
1. 访问网站后，网站Url自动添加一个5位的随机数在网址最后面，如 https://memo.chancel.ltd/73NSS ，73NSS即为便签ID
2. 写入文字/图片，网站会自动保存
3. 复制网站链接或记下网站链接的后5位数，在其他设备输入网址+5位随机数，即可访问刚才输入的内容

# 2. SyncMemo部署

## 2.1. 环境依赖

Python版本要求>3.5，依赖以下第三方库

``` shell
pip3 install flask PyYAML configparser
```

## 2.2. 快速部署

首先修改（创建）/opt/syncMemo//src/flaskr/conf/app.conf文件，文件作用如下

``` ini
[general]
# 允许便签最大大小
MEMO_MAX_SIZE = 5
# 便签保存间隔
SAVE_SPANTIME = 3000
```

然后运行以下命令可快速运行程序

``` shell
python3 /mnt/sda/Codes/dev/syncMemo/src/main.py -p 10923 --host 0.0.0.0
```

## 2.3. uWSGI/Nginx/Supervisor部署

### 2.3.1. uWSGI部署
建议采用uwsgi部署，部署环境参考如下

* 程序目录：/opt/syncMemo/

首先修改（创建）/opt/syncMemo//src/flaskr/conf/app.conf文件，文件作用如下

``` ini
[general]
# 允许便签最大大小
MEMO_MAX_SIZE = 5
# 便签保存间隔
SAVE_SPANTIME = 3000
```

然后安装uwsgi

``` Shell
pip install uWSGI
```

创建/opt/syncMemo/uwsgi配置文件

``` ini
[uwsgi]
module = main:app
master = true
processes = 2

chdir = /opt/syncMemo/src/
socket = /opt/syncMemo/uwsgi.sock
chmod-socket = 660
vacuum = true

die-on-term = true
```

运行uwsgi程序

``` 
uwsgi --ini /opt/syncMemo/uwsgi.ini
```

如输出没有error说明uWSGI部署成功

### 2.3.2. Nginx配置

uWSGI部分采用了SOCK文件的部署方式，Nginx的配置文件参考如下

``` conf
server {
    listen 443 ssl;
    server_name memo.chancel.ltd; #填写绑定证书的域名
    ssl_certificate ../1_memo.chancel.ltd_bundle.crt;
    ssl_certificate_key ../2_memo.chancel.ltd.key;
    ssl_session_timeout 5m;
    ssl_protocols TLSv1 TLSv1.1 TLSv1.2; #按照这个协议配置
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:HIGH:!aNULL:!MD5:!RC4:!DHE;#按照这个套件配置
    ssl_prefer_server_ciphers on;
    location / {
                include uwsgi_params;
                uwsgi_param    Host             $host;
                uwsgi_param    X-Real-IP        $remote_addr;
                uwsgi_param    X-Forwarded-For  $proxy_add_x_forwarded_for;
                uwsgi_param    HTTP_X_FORWARDED_FOR $remote_addr;
                proxy_redirect http:// https://;
                uwsgi_pass_request_headers on;
                uwsgi_pass unix:/opt/syncMemo/uwsgi.sock;
    }
}
server{
    listen 80;
    server_name memo.chancel.ltd;
    return 301 https://memo.chancel.ltd$request_uri;
}

```

### 2.3.3. Supervisor配置

uWSGI运行可使用 **nohup** 运行，也可以使用 **supervisor** 配置为daemon程序

supervisor配置文件参考如下

``` ini
[program:memo]
# directory=/opt/blog/src/
command=/home/chancel/.local/bin/uwsgi --ini /opt/syncMemo/uwsgi.ini
autostart=true
autorestart=true
startsecs=10
stdout_logfile=/var/log/supervisor/memo_stdout.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stdout_capture_maxbytes=1MB
stderr_logfile=/var/log/supervisor/memo_stderr.log
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=10
stderr_capture_maxbytes=1MB
user = apps
# environment = HOME="/home/git", USER="git"
```

# 3. SyncMemo开发

Python版本>3.5，并安装以下依赖

``` Shell
pip3 install flask PyYAML configparser
```

开发工具使用**Visual Studio Code（VSCode）**

参考启动的配置文件（LAUNCH. JSON）如下

``` Json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "port": 5001,
            "host": "0.0.0.0",
            "env": {
                "FLASK_APP": "${workspaceRoot}/src/main.py",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload",
                "--host=0.0.0.0",
                "--port=5000"
            ],
            "jinja": true
        }
    ]
}
```

# 感谢
编辑器来自 - [wangeditor](https://www.wangeditor.com/)
Web框架 - [Flask](https://github.com/pallets/flask)