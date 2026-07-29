# py_fisher

## 项目结构

```
py_fisher/
├── index.py                 # 入口：uvicorn 启动 FastAPI（dev 8010 + reload）
├── app/                     # 主应用代码
│   ├── __init__.py          # create_app、生命周期、注册路由与静态资源
│   ├── secure.py            # 环境变量加载（.env → .env.{APP_ENV}）
│   ├── setting.py           # 业务常量（分页、豆子、验证码 TTL 等）
│   ├── database.py          # SQLModel 引擎、Session、auto_commit
│   │
│   ├── web/                 # HTTP 路由层（前缀 /web）
│   │   ├── __init__.py      # web_router，汇总挂载各模块路由
│   │   ├── auth.py          # 登录 / 注册 / 找回密码
│   │   ├── book.py          # 图书相关
│   │   ├── product.py       # 商品相关
│   │   ├── gift.py          # 赠送清单
│   │   ├── wish.py          # 索要
│   │   ├── drift.py         # 漂流（赠送流转）
│   │   └── index.py         # 首页等
│   │
│   ├── models/              # ORM 表模型（Alembic 据此迁移）
│   │   ├── base.py          # BaseModel、软删除 SoftDeleteMixin
│   │   ├── user.py          # 用户
│   │   ├── book.py          # 图书
│   │   ├── gift.py          # 赠送
│   │   ├── wish.py          # 索要
│   │   └── drift.py         # 漂流记录
│   │
│   ├── forms/               # 请求体验证（Pydantic，入参校验）
│   ├── schemas/             # API 数据结构（响应体、分页、ApiResponse 等）
│   ├── services/            # 业务逻辑（写库、扣豆子、状态流转等）
│   ├── view_models/         # 组装返回给前端的视图数据
│   ├── deps/                # FastAPI 依赖（当前用户、按 id 查资源等）
│   ├── libs/                # 通用工具（JWT、Redis、邮件、异常、HTTP 客户端等）
│   ├── errors/              # 全局异常处理（统一 HTTP / body.code）
│   ├── spider/              # 第三方数据源抓取（如鱼书 API）
│   └── templates/           # HTML 模板（邮件、找回密码页等）
│
├── alembic/                 # 数据库迁移（versions/ 下放迁移脚本）
├── docker/                  # Docker Compose、Dockerfile、entrypoint
├── test/                    # 练习脚本 + 非生产调试路由（test_router）
├── requirements.txt         # 生产依赖
├── requirements-dev.txt     # 开发 / 测试依赖（pytest、httpx）
├── pyproject.toml           # Ruff 配置
├── alembic.ini
├── stop.ps1                 # 本地停端口脚本
└── .env.example             # 环境变量模板
```

---

## 快速开始

### 首次本地配置（最短路径）

1. Python **3.14** 创建并激活 venv（见「Python 版本」）
2. `pip install -r requirements.txt`
3. 复制环境模板：
   - 复制 `.env.example` → `.env.dev`，填入真实 `DATABASE_URL` / JWT / Redis / 邮箱 / `AppKey` / `YU_SHU_API_BASE`
   - 新建 `.env`，内容仅一行：`APP_ENV=dev`
4. 确认 MySQL 已建库、Redis 已启动
5. 表结构（空库或可重建的开发库）：

```powershell
alembic upgrade head
```
6.自检配置： `python(.\venv\Scripts\python.exe) -c "from app.secure import APP_ENV, DATABASE_URL; print(APP_ENV, DATABASE_URL[:40])"`
7.启动:
```powershell
alembic upgrade head
```

##  本地启动
1.创建虚拟环境并激活，安装依赖：
```powershell
py -3.14 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
# 或：.\venv\Scripts\python.exe -m pip install -r requirements.txt
```
2.按照 env.example 配置环境变量
生成 JWT KEY
```powershell
python -c "import secrets; print(secrets.token_urlsafe(64))"
```
3.启动本地 MySQL 和 Redis
4.初始化数据库表：`alembic upgrade head`
5.启动服务：`python(.\venv\Scripts\python.exe) index.py`
6.退出虚拟环境：`deactivate`
`
确认是否在本虚拟环境tips: python -c "import sys; print(sys.executable)"
`

## Docker 一键启动
在 docker 目录下：
1.复制 docker/.env.docker.example → docker/.env.docker，填入真实配置
（MYSQL_* 与 DATABASE_URL 中的用户/密码/库名须一致）
2.`docker compose up -d --build`

## 统一状态码
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

业务异常：AppError 抛出来
成功返回：ApiResponse 格式返回

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

## Ruff 使用
` 本项目用 [Ruff](https://docs.astral.sh/ruff/) 做 **代码格式化** 和 **基础 lint**。配置见根目录 `pyproject.toml`。`
1.安装
```
pip install ruff
pip freeze | findstr ruff # 写入requirement
```
2.格式化
`tips: 配置 .vscode/settings.json：Python 文件保存时自动用 Ruff 格式化,需安装ruff扩展`
```
ruff format . - 格式化整个项目（推荐在仓库根目录执行）
ruff format app/ - # 只格式化某个目录/文件
ruff format app/web/auth.py
ruff format --check . - # 仅检查，不修改文件（CI 可用）
```
3. Lint
当前只开启 E（pycodestyle）、F（pyflakes）规则；E501（行长）、E712（== False）已忽略。
```
# 检查
ruff check .

# 自动修复可修复项
ruff check --fix .
```