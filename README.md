用于同步文本图片的便签式 Web 服务，方便在 PC 和 移动设备之间同步文字图片信息

Demo：[memo.chancel.me](https://memo.chancel.me)

使用方法
1. 访问本站会分配一个随机数，例如 1234 ，点击确认开始编辑内容
2. 编辑完成后，在任意设备上访问本站并输入相同ID，即可查看相同的便签内容

功能
* 富文本编辑（图片/文字）
* 二维码分享
* 纯文本分享（不可编辑）
* 服务端支持配置文件自定义便签长度、大小、存储时间等

# 1. 部署
推荐 Docker 部署

## 1.1. Docker部署(推荐)

克隆本仓库到本地后，使用 docker 生成镜像

```bash
sudo docker build -t syncmemo:latest . --no-cache
```

复制一份配置文件，根据需要自行修改 `./config.yaml` 的内容
```bash
copy .config.yaml config.yaml
```

运行镜像
```bash
docker run -v ./config.yaml:/app/config.yaml -p 8000:80 syncmemo:latest
```

访问 http://localhost:8000 查看效果


## 1.2. 源码部署（gunicorn）

源码运行需要安装Python环境，以下部署基于`Python 3.8.6`，请在部署前确认已安装 Python 环境

克隆仓库，并切换到仓库路径下
```bash
git clone https://github.com/chancelyg/syncmemo.git && cd syncmemo
```

安装依赖
``` shell
pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple
```

复制一份配置文件，根据需要自行修改 `./config.yaml` 的内容
```bash
copy .config.yaml config.yaml
```

运行程序
```bash
gunicorn --env CONFIG=config.yaml flaskr:app
```

访问 http://localhost:8000 查看效果

# 2. 数据保存

数据的保存有效期取决于 `config.yaml` 文件中的 `memo/expire` 值（单位为秒），设该值为 `0` 时，数据将永不过期

便签保存于 `config.yaml` 配置中的 `system/cache` 中

如 Docker 部署需要持久化数据，则将 `config.yaml` 中的 `system/cache` 映射出来，如：

```bash
docker run -v ./config.yaml:/app/config.yaml -v ./cache:/app/cache -p 8000:80 syncmemo:latest
```

# 3. SyncMemo开发环境

Python 版本 3.8.6 ，并安装依赖：

``` Shell
pip3 install -r requirements.txt -i https://pypi.doubanio.com/simple
```

开发工具使用**Visual Studio Code（VSCode）**

参考启动的配置文件 `.vscode/launch.json`如下

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
                "CONFIG": "${workspaceRoot}/conf/.config.yam;"
            },
            "args": [
                "run",
                "--host=127.0.0.1",
                "--port=8000",
            ],
            "jinja": true
        }
    ]
}
```

按下 `F5` 启动项目，并访问 http://127.0.0.1:8000 查看效果

# 4. 感谢

项目技术依赖来源：
* [quilljs - Your powerful rich text editor.](https://quilljs.com/)
* [Flask - Flask is a lightweight WSGI web application framework](https://github.com/pallets/flask)
* [Mdui - MDUI 漂亮、轻量且好用，它能让你更轻松地开发 Material Design 网页应用](https://www.mdui.org)
* [Vuejs - The Progressive JavaScript Framework](https://vuejs.org/)

项目基于以上的开源项目进行开发