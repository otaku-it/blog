# Baize.dev 技术博客

一个可直接运行的前后端分离技术博客系统。页面保留清爽、偏科技的产品原型视觉，但文章、草稿、标签、分类和评论已经接入 MySQL 持久化，不依赖浏览器内存或静态 mock 数据。

- 前端：Vue 3、Vue Router、Vite、Tailwind CSS
- 后端：Python、FastAPI、SQLAlchemy、Alembic
- 数据库：已有 MySQL 8.x（utf8mb4），Docker Compose 不再创建 MySQL 容器
- 部署：Docker Compose、Nginx
- API：文章分页/筛选/搜索、草稿发布、标签分类、评论、健康检查
- 权限：管理员登录后才能进入内容后台、保存草稿或发布文章

## Docker Compose 启动

```bash
cp .env.example .env
# 配置现有 MySQL 的地址、数据库名和账号密码，并修改 ADMIN_PASSWORD、AUTH_SECRET
docker compose up -d --build
```

打开 <http://localhost:18080>，API 文档位于 <http://localhost:18080/api/docs>。

如需使用其他端口：

```bash
BLOG_PORT=9000 docker compose up -d --build
```

Docker Compose 只启动前端和后端，不创建新的 MySQL 容器。后端通过 `.env` 中的 `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_DATABASE`、`MYSQL_USER` 和 `MYSQL_PASSWORD` 连接已有 MySQL；如果 MySQL 就运行在 Docker 宿主机，默认的 `host.docker.internal` 可以直接使用。首次连接目标库时，后端会自动执行 Alembic 数据库迁移，并在完全空的业务表中写入初始化数据。

云服务器现有 MySQL 使用宿主机端口时，配置示例：

```env
MYSQL_HOST=host.docker.internal
MYSQL_PORT=3308
MYSQL_DATABASE=blog
MYSQL_USER=root
MYSQL_PASSWORD=实际密码
```

后端启动时会先等待现有 MySQL 可用；如果配置的业务数据库不存在，会在这个已有 MySQL 实例内执行 `CREATE DATABASE IF NOT EXISTS`，随后通过 Alembic 创建或升级数据表。它不会启动新的 MySQL 容器，也不会删除已有数据库或表。日志会显示连接的主机、端口和数据库名，但不会打印数据库密码。

数据库结构以 Alembic 迁移为准：

- 初始表结构：[backend/alembic/versions/0001_initial.py](backend/alembic/versions/0001_initial.py)
- 管理员和站点资料：[backend/alembic/versions/0002_admin_profile.py](backend/alembic/versions/0002_admin_profile.py)
- 后续字段升级：`backend/alembic/versions/0003_*.py` 至 `0007_*.py`
- 完整 MySQL 8 建表参考脚本：[backend/sql/schema.sql](backend/sql/schema.sql)

已有数据库推荐直接执行迁移，不要重复运行完整建表脚本：

```bash
cd backend
DATABASE_URL='mysql+pymysql://用户名:密码@主机:3306/数据库名?charset=utf8mb4' .venv/bin/alembic upgrade head
```

管理员登录页不在公共导航中展示，需要直接访问 `/admin/login`。管理员账号由 `.env` 中的 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 初始化，默认账号名为 `baize`；首次初始化后可在“后台 → 站点设置 → 登录密码”中修改密码。未登录用户不能创建、修改或读取草稿，公开页面只能看到已发布文章。

后台支持维护“关于我”资料、个人原则、技术栈、文章分类和标签。分类、标签均可新增和改名，只有没有关联文章的空分类或空标签允许删除。文章支持新建、编辑、保存草稿、发布和二次确认删除。

查看服务状态和日志：

```bash
docker compose ps
docker compose logs -f backend frontend
```

停止服务但保留数据：

```bash
docker compose down
```

`docker compose down` 或 `docker compose down -v` 都不会删除外部 MySQL 数据；`-v` 只会删除本项目的上传资源卷，请谨慎使用。

## 本地开发

后端：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

本地开发默认使用 `sqlite:///./blog.db`，便于运行测试；生产/Compose 环境通过 `DATABASE_URL` 使用已有 MySQL。需要本地连接 MySQL 时，导出对应连接串即可。

前端：

```bash
cd frontend
npm install
npm run dev
```

Vite 会把 `/api` 代理到 `http://localhost:8000`。
