.PHONY: help build up down restart logs shell db-shell redis-shell clean

# 默认目标
help: ## 显示帮助信息
	@echo "可用的命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## 构建 Docker 镜像
	docker-compose build

up: ## 启动所有服务
	docker-compose up -d

dev: ## 启动开发环境（前台运行，显示日志）
	docker-compose up

down: ## 停止所有服务
	docker-compose down

restart: ## 重启所有服务
	docker-compose restart

logs: ## 查看所有服务日志
	docker-compose logs -f

logs-api: ## 查看 API 服务日志
	docker-compose logs -f api

logs-frontend: ## 查看前端服务日志
	docker-compose logs -f frontend

shell: ## 进入 API 容器 shell
	docker-compose exec api bash

frontend-shell: ## 进入前端容器 shell
	docker-compose exec frontend bash

db-shell: ## 进入数据库 shell
	docker-compose exec db psql -U postgres -d myapi_dev

redis-shell: ## 进入 Redis shell
	docker-compose exec redis redis-cli

init-db: ## 初始化数据库
	docker-compose exec api python scripts/init_db.py

seed-data: ## 填充种子数据
	docker-compose exec api python scripts/seed_data.py

migrate: ## 运行数据库迁移
	docker-compose exec api flask db upgrade

migration: ## 创建新的数据库迁移
	docker-compose exec api flask db migrate -m "$(MSG)"

clean: ## 清理 Docker 资源
	docker-compose down
	docker system prune -f

clean-all: ## 清理所有 Docker 资源（包括镜像）
	docker-compose down --rmi all
	docker system prune -af

status: ## 查看服务状态
	docker-compose ps

health: ## 检查服务健康状态
	@echo "=== API Health ==="
	@curl -f http://localhost:15000/health || echo "API 不可用"
	@echo -e "\n=== Frontend Health ==="
	@curl -f http://localhost:18080/ || echo "前端不可用"
	@echo -e "\n=== Database Health ==="
	@docker-compose exec db pg_isready -U postgres || echo "数据库不可用"
	@echo -e "\n=== Redis Health ==="
	@docker-compose exec redis redis-cli ping || echo "Redis 不可用"

install: ## 安装依赖（在容器内）
	docker-compose exec api pip install -r requirements.txt

freeze: ## 更新 requirements.txt
	docker-compose exec api pip freeze > requirements.txt

backup-db: ## 备份数据库
	docker-compose exec db pg_dump -U postgres myapi_dev > backup_$(shell date +%Y%m%d_%H%M%S).sql

restore-db: ## 恢复数据库（需要指定 FILE=backup.sql）
	@if [ -z "$(FILE)" ]; then echo "请指定备份文件: make restore-db FILE=backup.sql"; exit 1; fi
	cat $(FILE) | docker-compose exec -T db psql -U postgres myapi_dev

update-frontend: ## 更新前端文件
	@echo "请将前端打包文件复制到 /opt/webapp-frontend/dist/ 目录"
	@echo "然后执行: docker-compose restart frontend"

setup-dirs: ## 创建必要的目录
	@echo "创建前端部署目录..."
	sudo mkdir -p /opt/webapp-frontend/dist
	sudo chown $$USER:$$USER /opt/webapp-frontend -R
	@echo "创建数据持久化目录..."
	mkdir -p /data/{postgres,redis}
	@echo "目录创建完成！"