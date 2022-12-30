用于多设备同步文本/图片的便签Web服务，方便在PC、Android、IOS之间同步文字图片信息

Demo使用体验： [memo.chancel.me](https://memo.chancel.me)

使用效果如图
![](https://image.chancel.me/2022/04/08/e289570993967.gif)

使用方法
1. 访问本站时会自动分配一个随机数（类似于1234），花几秒钟记住这个ID，点击确认接着开始编辑便签
2. 编辑便签内容后，在任意可以访问互联网的设备上输入本站网址，并输入上一步中记住的ID，即可获得相同的便签内容

功能
* 富文本编辑（图片/文字）
* 二维码分享
* 纯文本分享
* 服务端支持配置文件自定义便签长度、大小、存储时间等

# 1. 部署
推荐Docker部署，简单方便，源码部署需要一定的Linux基础

## 1.1. Docker部署(推荐)
克隆本仓库到本地后，使用docker 生成镜像
```bash
sudo docker build -t syncmemo:latest . --no-cache
```

运行镜像（端口7900根据需要自行修改）
```bash
docker run -d --name syncmemo -p 7900:80 syncmemo:latest
```

## 1.2. 源码部署（gunicorn）

源码运行需要安装Python环境，请自行安装，以下部署基于`Python 3.8.6`

> 安装Python环境参考 [在Linux下手动编译安装指定的Python版本](https://www.chancel.me/notes/52)

克隆仓库，并切换到仓库路径下
```bash
git clone https://github.com/chancelyg/syncmemo.git && cd syncmemo
```

安装依赖
``` shell
pip3 install -r requirements.txt && pip3 install gunicorn
```

创建`app.conf`文件，内容可参考`app.conf.example`

运行gunicorn程序

```bash
gunicorn -w 1 -b 127.0.0.1:7900 --env MEMO_CONF=conf/app.conf flaskr:"create_app()"
```

访问 http://127.0.0.1:7900 即可看到便签首页


# 2. SyncMemo开发环境

Python版本3.8.6，并安装以下依赖

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
            "console": "internalConsole",
            "python": "/home/chancel/codes/python/SyncMemo/venv/bin/python",
            "env": {
                "FLASK_APP": "${workspaceRoot}/flaskr",
                "FLASK_ENV": "development",
                "FLASK_DEBUG": "1",
                "MEMO_CONF": "${workspaceRoot}/conf/app.conf"
            },
            "args": [
                "run",
                "--host=127.0.0.1",
                "--port=7900",
            ],
            "jinja": true
        }
    ]
}
```

# 3. 感谢

项目技术依赖
* [wangeditor - Typescript 开发的 Web 富文本编辑器， 轻量、简洁、易用、开源免费](https://www.wangeditor.com/)
* [Flask - Flask is a lightweight WSGI web application framework](https://github.com/pallets/flask)
* [Mdui - MDUI 漂亮、轻量且好用，它能让你更轻松地开发 Material Design 网页应用](https://www.mdui.org)
* [Vuejs - The Progressive JavaScript Framework](https://vuejs.org/)

项目基于以上的开源项目，感谢！