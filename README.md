替代登录微信来同步文本/图片的开源便签web程序，方便不同设备（PC、Android、IOS）之间同步文字图片信息

使用体验： [memo.chancel.me](https://memo.chancel.me)

![](https://image.chancel.me/2022/04/08/e289570993967.gif)


使用方法
1. 访问本站时会自动分配一个随机数（类似于ABCD），稍微花几秒钟记住这个ID，点击确认开始编辑便签
2. 编辑便签内容后（支持文字/图片），在任意可以访问本站的设备上输入本站网址，并输入上一步中记住的ID，即可获得相同的便签内容

功能
* 富文本编辑（图片/文字）
* 二维码分享
* 纯文本分享
* 服务端支持配置文件自定义便签长度、大小、存储时间等

# 1. 部署
推荐Docker部署，简单方便，源码部署需要一定的Linux基础

## 1.1. Docker部署(推荐)
拉取Docker镜像
```bash
sudo docker pull chancelyang/syncmemo:v1.3.0
```

运行镜像（端口7900根据需要自行修改）
```bash
docker run -d --name syncmemo -p 7900:7900 chancelyang/syncmemo:v1.3.0
```

如需修改配置，可进入容器修改`/app/syncmemo.conf`后重启容器
```bash
sudo docker exec -i -t [container_id] /bin/sh
```

## 1.2. 源码部署（gunicorn）

源码运行需要安装Python环境，请自行安装，以下部署基于`Python 3.7.2`

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
gunicorn -w 2 -b 0.0.0.0:7900 --env MEMO_CONF=conf/app.conf 'flaskr:create_app()
```

访问 http://127.0.0.1:7900 即可看到便签首页


# 2. SyncMemo开发环境

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

# 3. 感谢

项目技术依赖
* [wangeditor - Typescript 开发的 Web 富文本编辑器， 轻量、简洁、易用、开源免费](https://www.wangeditor.com/)
* [Flask - Flask is a lightweight WSGI web application framework](https://github.com/pallets/flask)
* [Mdui - MDUI 漂亮、轻量且好用，它能让你更轻松地开发 Material Design 网页应用](https://www.mdui.org)
* [Vuejs - The Progressive JavaScript Framework](https://vuejs.org/)

项目基于以上的开源项目，感谢！