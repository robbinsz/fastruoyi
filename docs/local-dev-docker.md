# Local Dev With Docker Services

## Goal

本地跑前端和后端源码，数据库与 Redis 直接连接现有 Docker 容器映射端口，和生产部署容器环境分开。

## Ports

- Docker 前端：`12580`
- Docker 后端：`19099`
- Docker MySQL：`13306`
- Docker Redis：`16379`
- 本地后端开发环境：`19100`
- 本地前端开发环境：`18080`

## Backend

使用新增环境文件 [`.env.localdocker`](/Users/robbins/paywww/fastruoyi/ruoyi-fastapi-backend/.env.localdocker)：

```bash
cd /Users/robbins/paywww/fastruoyi/ruoyi-fastapi-backend
uv venv --python 3.10
uv pip install --python .venv/bin/python -r requirements.txt
.venv/bin/python app.py --env=localdocker
```

说明：
- 数据库连接 `127.0.0.1:13306`
- Redis 连接 `127.0.0.1:16379`
- 本地后端地址：`http://127.0.0.1:19100`
- Swagger：`http://127.0.0.1:19100/dev-api/docs`

## Frontend

使用新增环境文件 [`.env.localdocker`](/Users/robbins/paywww/fastruoyi/ruoyi-fastapi-frontend/.env.localdocker)：

```bash
cd /Users/robbins/paywww/fastruoyi/ruoyi-fastapi-frontend
pnpm install
pnpm run dev:localdocker
```

说明：
- 本地前端地址：`http://127.0.0.1:18080`
- `/dev-api` 会代理到 `http://127.0.0.1:19100`
- 不影响 Docker 前端 `12580`

## Recommended Workflow

1. 保持 Docker MySQL、Redis 运行。
2. 停掉 Docker 后端和 Docker 前端，避免误用旧代码：

```bash
docker stop ruoyi-backend-my ruoyi-frontend
```

3. 启动本地后端。
4. 启动本地前端。
5. 浏览器访问 `http://127.0.0.1:18080` 做联调。

首次使用前先安装依赖：

```bash
cd /Users/robbins/paywww/fastruoyi
make install-backend
make install-frontend
```

前端现在使用 `pnpm` 管理依赖和启动命令。

后端现在使用 `uv` 创建和管理虚拟环境：
- 虚拟环境目录：`ruoyi-fastapi-backend/.venv`
- Python 版本文件：[.python-version](/Users/robbins/paywww/fastruoyi/ruoyi-fastapi-backend/.python-version)
- 一键初始化脚本：[setup-backend-uv.sh](/Users/robbins/paywww/fastruoyi/scripts/setup-backend-uv.sh)

也可以直接使用脚本：

```bash
/Users/robbins/paywww/fastruoyi/scripts/run-backend-localdocker.sh
/Users/robbins/paywww/fastruoyi/scripts/run-frontend-localdocker.sh
```

或者直接使用仓库根目录 `Makefile`：

```bash
cd /Users/robbins/paywww/fastruoyi
make dev-up
```

常用命令：

```bash
make dev-up
make dev-stop
make dev-logs
make dev-backend
make dev-frontend
```
