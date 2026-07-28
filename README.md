# web目录放路由
# models目录放模型设计，用来建表
# libs - 辅助函数
# setting文件 - 常用变量


# 首次拉取代码启动项目
## 1）本地启动
```
1、创建虚拟环境并激活，安装依赖
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt(.\venv\Scripts\python.exe（python） -m pip install -r requirements.txt)

2、按照env.example配置环境变量
生成JWT KEY: python -c "import secrets; print(secrets.token_urlsafe(64))"

3、启动本地 MySQL 和 Redis

4. 初始化数据库表：alembic upgrade head

5、启动服务：.\venv\Scripts\python.exe index.py

6、退出虚拟环境：deactivate

（确认是否是在本虚拟环境，python -c "import sys; print(sys.executable)"）

```

## 2）docker一键启动
```
docker 目录下：
1. 复制 docker/.env.docker.example → docker/.env.docker，填入真实配置
   （MYSQL_* 与 DATABASE_URL 中的用户/密码/库名须一致）
2. docker compose up -d --build
3. 访问 http://localhost:8010/docs
```


# 1、确认本地数据库已经连接

# 2、确认redis已连接
## 1）启动docker中的redis-dev容器
## 2）连接redis - docker exec -it redis-dev redis-cli - 暂时不用

# 3、启动项目
## 1）cd fisher
## 2）激活虚拟环境 .\venv\Scripts\Activate.ps1
## 3）启动命令  .\venv\Scripts\python.exe index.py


# 安装包需要写入requirements.txt
```
python -m pip install 包名
pip freeze | findstr 包名
将打印出的报名写入requirements.txt
```

# 启动无法加载检查端口是否被占用
```
reload=True 时 uvicorn 会起 两个进程：

父进程：文件监听（reloader）
子进程：真正跑 FastAPI 的 worker

端口问题-停端口
netstat -ano | findstr ":8000"
Stop-Process -Id 2884 -Force

一键停掉80端口：
在项目目录下打开 PowerShell：
.\stop.ps1 -- Stopped python (PID=21188)
```

# 统一状态码
```
成功：HTTP 200，body.code = 0
业务错误：HTTP 400，body.code = 400
未登录/登录过期：HTTP 401，body.code = 401
参数错误：HTTP 422，body.code = 422
服务端错误：HTTP 500，body.code = 500
第三方服务错误：HTTP 502，body.code = 502

前端处理：
code === 0    成功
code === 401  跳登录
其他 code     直接 toast message

业务异常：AppError抛出来
成功返回：ApiResponse格式返回

业务错误：AppError 默认改为业务错误：code=400、HTTP 400。
成功返回：成功响应统一使用 ApiResponse 默认 code=0，

全局异常处理统一：
参数错误：422
数据写入错误：400
数据库/服务端错误：500
HTTP 异常：body code 等于 HTTP status
保留特殊状态：
未登录/用户不存在登录态：401
发送过于频繁：429

```

# 数据库迁移（Alembic）

改表不要靠启动时 create_all，按下面流程：

1. 修改 `app/models/*.py`
2. 生成迁移：`alembic revision --autogenerate -m "说明这次改了什么"`
3. **打开** `alembic/versions/` 下新文件检查：只保留本次真正需要的变更，删掉误报的 drop/alter
4. 执行：`alembic upgrade head`
5. 提交时：模型文件 + `alembic/versions/xxx.py` 一起提交

常用命令（在 `fisher/` 目录、已激活 venv）：

```powershell
alembic current
alembic upgrade head
alembic downgrade -1
```

环境变量见 `.env.example`。本地用 `APP_ENV=dev`；生产用 `APP_ENV=prod`（表结构走 Alembic，启动时不 create_all）。

# Python 版本

本地与生产统一使用 **Python 3.14**（见 `.python-version`）。  
创建 venv 时请使用 `python3.14 -m venv venv`，勿用系统自带的 3.10。

后续计划：用 Docker 固定同一运行时（上线完成后再配置）。

# 环境配置（dev / staging / prod）

文件约定：

| 文件 | 作用 | 是否进 Git |
|------|------|------------|
| `.env` | 只写 `APP_ENV=dev`（或 staging/prod） | 否 |
| `.env.dev` | 本地完整配置 | 否 |
| `.env.staging` / `.env.prod` | 预发/生产完整配置（可选；生产更推荐平台注入） | 否 |
| `.env.example` | 模板说明 | 是 |

加载顺序（`app/secure.py`）：先 `.env`，再 `.env.{APP_ENV}`。进程里已有的环境变量优先（方便测试 / Docker）。

本地切换：

1. 准备好对应的 `.env.dev`（或 `.env.staging`）
2. 修改 `.env` 中的 `APP_ENV=...`
3. **重启** `index.py` / uvicorn

```powershell
# 自检当前环境
.\venv\Scripts\python.exe -c "from app.secure import APP_ENV, SQL_ECHO, DATABASE_URL; print(APP_ENV, SQL_ECHO, DATABASE_URL[:40])"
```

# 首次本地配置（最短路径）
1. Python **3.14** 创建并激活 venv（见下方「Python 版本」）
2. `pip install -r requirements.txt`
3. 复制环境模板：
   - 复制 `.env.example` → `.env.dev`，填入真实 `DATABASE_URL` / JWT / Redis / 邮箱 / `AppKey` / `YU_SHU_API_BASE`
   - 新建 `.env`，内容仅一行：`APP_ENV=dev`
4. 确认 MySQL 已建库、Redis 已启动
5. 表结构（空库或可重建的开发库）：
   ```powershell
   alembic upgrade head
6. 自检配置：`.\venv\Scripts\python.exe -c "from app.secure import APP_ENV, DATABASE_URL; print(APP_ENV, DATABASE_URL[:40])"`
7. 启动：`.\venv\Scripts\python.exe index.py`


# ruff 使用
` 本项目用 [Ruff](https://docs.astral.sh/ruff/) 做 **代码格式化** 和 **基础 lint**。配置见根目录 `pyproject.toml`。`
## 安装
```
pip install ruff
pip freeze | findstr ruff # 写入requirement
```
## 格式化
`
ruff format . - 格式化整个项目（推荐在仓库根目录执行）
ruff format app/ - # 只格式化某个目录/文件
ruff format app/web/auth.py
ruff format --check . - # 仅检查，不修改文件（CI 可用）
`
## Lint
当前只开启 E（pycodestyle）、F（pyflakes）规则；E501（行长）、E712（== False）已忽略。
```
# 检查
ruff check .

# 自动修复可修复项
ruff check --fix .
```
