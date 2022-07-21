# 1. SyncMemo

一个支持跨平台同步文本/图片的开源便签程序，基于Python的Flask框架开发

![](https://image.chancel.me/2022/04/08/e289570993967.gif)

* 项目Demo：[https://memo.chancel.me](https://memo.chancel.me)
* 使用帮助：[https://memo.chancel.me/help](https://memo.chancel.me/help)

使用方法
1. 访问本站时会自动分配一个随机数（类似于ABCD），稍微花几秒钟记住这个ID，点击确认开始编辑便签
2. 编辑便签内容后（支持文字/图片），在任意可以访问本站的设备上输入本站网址，并输入上一步中记住的ID，即可获得相同的便签内容

功能
* 富文本编辑（图片/文字）
* 二维码分享
* 纯文本分享
* 服务端支持配置文件自定义便签长度、大小、存储时间等

项目依赖
* Python（版本大于3，开发使用版本3.7.2）

# 2. SyncMemo部署


## 2.1. 使用Python运行（方法一）
克隆仓库，并切换到仓库路径下
```bash
git clone https://github.com/chancelyg/syncmemo.git && cd syncmemo
```

安装依赖
``` shell
pip3 install -r requirements.txt
```

创建conf/app.conf文件，文件内容可参考conf/app.conf.example

``` ini
cat conf/app.conf

[general]
HOST = 0.0.0.0
PORT = 7900

[memo]
# 允许便签最大大小
MEMO_MAX_SIZE = 5
# 便签保存间隔
SAVE_SPANTIME = 5000
# 便签ID长度
MEMO_ID_LENGTH = 4
LOCAL_STORE_LENGTH = 10

[log]
PATH = /var/log/memo
LEVEL = DEBUG

[store]
PATH = data/cache
TIMEOUT_DAY = 14
```

运行程序

``` shell
python3 src/main.py -c conf/app.conf
```

访问 http://127.0.0.1:7900 即可看到便签首页

## 2.2. Docker运行（方法二）
仓库根目录下有Dockerfile文件，使用Docker生成镜像后可运行容器，具体步骤如下

复制conf/app.conf.example到仓库目录下，重命名为app.conf

并根据实际情况修改app.conf，Docker部署需注意以下2个值
* HOST：必须为0.0.0.0
* PROT：必须与Docker中的EXPOSE值一致（无特殊要求则默认7900）

```bash
cp conf/app.conf.example ./app.conf

[general]
HOST = 0.0.0.0
PORT = 7900 

[memo]
# 允许便签最大大小
MEMO_MAX_SIZE = 5
# 便签保存间隔
SAVE_SPANTIME = 5000
# 便签ID长度
MEMO_ID_LENGTH = 4
LOCAL_STORE_LENGTH = 10

[log]
PATH = /var/log/memo
LEVEL = DEBUG

[store]
PATH = data/cache
TIMEOUT_DAY = 14
```

生成镜像
```bash
docker build -t chancel/syncmemo:latest . --no-cache
```

查看镜像
```bash
docker images

# 输出如下
REPOSITORY         TAG                IMAGE ID       CREATED         SIZE
chancel/syncmemo   latest             697ff7567b79   5 days ago      325MB
...
```

运行镜像
```bash
docker run -d --name syncmemo -p 7900:7900 syncmemo:latest
```

查看容器的运行情况
```bash
sudo docker container ls

# 输出
CONTAINER ID   IMAGE             COMMAND                  CREATED          STATUS          PORTS                                         NAMES
1f8504b20688   syncmemo:latest   "/usr/local/python3.…"   29 minutes ago   Up 29 minutes   0.0.0.0:7900->7900/tcp, :::7900->7900/tcp     syncmemo
...
```

访问 http://127.0.0.1:7900 即可看到便签首页

## 2.3. uWSGI+Supervisor部署（方法三）

### 2.3.1. uWSGI部署
克隆仓库，并切换到仓库路径下
```bash
git clone https://github.com/chancelyg/syncmemo.git && cd syncmemo
```

安装依赖
``` shell
pip3 install -r requirements.txt && pip3 install uwsgi
```

创建conf/app.conf文件，文件内容可参考conf/app.conf.example

``` ini
cat conf/app.conf

[general]
HOST = 0.0.0.0
PORT = 7900

[memo]
# 允许便签最大大小
MEMO_MAX_SIZE = 5
# 便签保存间隔
SAVE_SPANTIME = 5000
# 便签ID长度
MEMO_ID_LENGTH = 4
LOCAL_STORE_LENGTH = 10

[log]
PATH = /var/log/memo
LEVEL = DEBUG

[store]
PATH = data/cache
TIMEOUT_DAY = 14
```

运行uwsgi程序

```bash
uwsgi -w main:create_app() --socket=0.0.0.0:7900 --protocol=http --chdir='src' --pyargv='-c ../conf/app.conf'
```

访问 http://127.0.0.1:7900 即可看到便签首页

## 2.4. Deamon与Nginx

### 2.4.1. Supervisor配置

uWSGI运行可使用 **nohup** 运行，更推荐使用Deamon方式来部署

以下是使用**supervisor**将syncmemo配置为daemon程序

supervisor配置文件参考如下

``` ini
[program:memo]
command=/home/chancel/.local/bin/uwsgi --ini /srv/syncmemo/uwsgi.ini
autostart=true
autorestart=true
startsecs=10
stdout_logfile=/var/log/supervisor/syncmemo_stdout.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=10
stdout_capture_maxbytes=1MB
stderr_logfile=/var/log/supervisor/syncmemo_stderr.log
stderr_logfile_maxbytes=10MB
stderr_logfile_backups=10
stderr_capture_maxbytes=1MB
user = apps
```

### 2.4.2. Nginx配置

uWSGI部分可采用了本地SOCK文件与Nginx通信的的部署方式

新建一个uwsgi.ini文件，内容如下
```ini
[uwsgi]
module = main:create_app()
master = true
processes = 1
pyargv=-c /srv/memo/syncmemo/conf/app.conf

chdir = /srv/memo/syncmemo/src/
socket = /srv/memo/uwsgi.sock
chmod-socket = 660
vacuum = true
```


Nginx的配置文件参考如下
``` conf
server {
    listen 7900;
    server_name memo.chancel.me; 
    location / {
                include uwsgi_params;
                uwsgi_param    Host             $host;
                uwsgi_param    X-Real-IP        $remote_addr;
                uwsgi_param    X-Forwarded-For  $proxy_add_x_forwarded_for;
                uwsgi_param    HTTP_X_FORWARDED_FOR $remote_addr;
                proxy_redirect http:// https://;
                uwsgi_pass_request_headers on;
                uwsgi_pass unix:/srv/syncmemo/uwsgi.sock;
    }
}

```

# 3. SyncMemo开发环境

Python版本3.7.2，并安装以下依赖

``` Shell
pip3 install -r requirements.txt
```

开发工具使用**Visual Studio Code（VSCode）**

参考启动的配置文件（LAUNCH. JSON）如下

``` Json
{
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

# 4. 感谢

项目技术依赖
* [wangeditor - Typescript 开发的 Web 富文本编辑器， 轻量、简洁、易用、开源免费](https://www.wangeditor.com/)
* [Flask - Flask is a lightweight WSGI web application framework](https://github.com/pallets/flask)
* [Mdui - MDUI 漂亮、轻量且好用，它能让你更轻松地开发 Material Design 网页应用](https://www.mdui.org)
* [Vuejs - The Progressive JavaScript Framework](https://vuejs.org/)

项目基于以上的开源项目，感谢！