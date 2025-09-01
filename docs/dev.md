## 数据库迁移
* 初始化迁移仓库(第一次)：`flask db init`
* 创建迁移文件：`flask db migrate -m "message"`
* 迁移：`flask db upgrade`

## 运行reids容器
```angular2html
docker run -d \
  --name my-redis \
  -p 6379:6379 \
  redis:latest \
  redis-server --requirepass mypassword
```