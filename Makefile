SHELL := /bin/bash

ROOT := $(CURDIR)
BACKEND_DIR := $(ROOT)/ruoyi-fastapi-backend
FRONTEND_DIR := $(ROOT)/ruoyi-fastapi-frontend
LOG_DIR := $(ROOT)/.logs
BACKEND_PY := $(BACKEND_DIR)/.venv/bin/python

.PHONY: help dev dev-backend dev-frontend dev-up dev-stop dev-logs install-backend install-frontend

help:
	@echo "Available targets:"
	@echo "  make dev            # 前台查看本地联调启动说明"
	@echo "  make dev-backend    # 前台启动本地后端开发环境"
	@echo "  make dev-frontend   # 前台启动本地前端开发环境"
	@echo "  make dev-up         # 后台一键启动本地前后端开发环境"
	@echo "  make dev-stop       # 停止本地前后端开发环境"
	@echo "  make dev-logs       # 查看本地联调日志位置"
	@echo "  make install-backend  # 安装后端依赖"
	@echo "  make install-frontend # 使用 pnpm 安装前端依赖"

dev:
	@echo "本地联调地址:"
	@echo "  Frontend: http://127.0.0.1:18080"
	@echo "  Backend : http://127.0.0.1:19100"
	@echo "  Swagger : http://127.0.0.1:19100/dev-api/docs"
	@echo ""
	@echo "推荐先确保 Docker MySQL/Redis 运行，再执行:"
	@echo "  make dev-up"

install-backend:
	cd $(BACKEND_DIR) && uv venv --python 3.10
	cd $(BACKEND_DIR) && uv pip install --python .venv/bin/python -r requirements.txt

install-frontend:
	cd $(FRONTEND_DIR) && pnpm install

dev-backend:
	@if [ ! -x "$(BACKEND_PY)" ]; then echo "Missing backend virtualenv. Run 'make install-backend' first."; exit 1; fi
	cd $(BACKEND_DIR) && .venv/bin/python app.py --env=localdocker

dev-frontend:
	@if [ ! -x "$(FRONTEND_DIR)/node_modules/.bin/vite" ]; then echo "Missing frontend dependencies. Run 'make install-frontend' first."; exit 1; fi
	cd $(FRONTEND_DIR) && pnpm run dev:localdocker

dev-up:
	@mkdir -p $(LOG_DIR)
	@if [ ! -x "$(BACKEND_PY)" ]; then echo "Missing backend virtualenv. Run 'make install-backend' first."; exit 1; fi
	@if [ ! -x "$(FRONTEND_DIR)/node_modules/.bin/vite" ]; then echo "Missing frontend dependencies. Run 'make install-frontend' first."; exit 1; fi
	@echo "Starting local backend on http://127.0.0.1:19100"
	@nohup bash -lc 'cd "$(BACKEND_DIR)" && .venv/bin/python app.py --env=localdocker' > "$(LOG_DIR)/backend-localdocker.log" 2>&1 & echo $$! > "$(LOG_DIR)/backend-localdocker.pid"
	@echo "Starting local frontend on http://127.0.0.1:18080"
	@nohup bash -lc 'cd "$(FRONTEND_DIR)" && pnpm run dev:localdocker' > "$(LOG_DIR)/frontend-localdocker.log" 2>&1 & echo $$! > "$(LOG_DIR)/frontend-localdocker.pid"
	@echo "Started."
	@echo "  Backend log : $(LOG_DIR)/backend-localdocker.log"
	@echo "  Frontend log: $(LOG_DIR)/frontend-localdocker.log"

dev-stop:
	@if [ -f "$(LOG_DIR)/backend-localdocker.pid" ]; then kill "$$(cat "$(LOG_DIR)/backend-localdocker.pid")" 2>/dev/null || true; rm -f "$(LOG_DIR)/backend-localdocker.pid"; fi
	@if [ -f "$(LOG_DIR)/frontend-localdocker.pid" ]; then kill "$$(cat "$(LOG_DIR)/frontend-localdocker.pid")" 2>/dev/null || true; rm -f "$(LOG_DIR)/frontend-localdocker.pid"; fi
	@echo "Stopped local dev processes if they were running."

dev-logs:
	@echo "Backend log : $(LOG_DIR)/backend-localdocker.log"
	@echo "Frontend log: $(LOG_DIR)/frontend-localdocker.log"
