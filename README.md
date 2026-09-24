# Baize.dev 技术博客

一个可直接运行的前后端分离技术博客系统。页面保留清爽、偏科技的产品原型视觉，但文章、草稿、标签、分类和评论已经接入 MySQL 持久化，不依赖浏览器内存或静态 mock 数据。

- 前端：Vue 3、Vue Router、Vite、Tailwind CSS
- 后端：Python、FastAPI、SQLAlchemy、Alembic
- 数据库：MySQL 8.4（utf8mb4）
- 部署：Docker Compose、Nginx
- API：文章分页/筛选/搜索、草稿发布、标签分类、评论、健康检查
- 权限：管理员登录后才能进入内容后台、保存草稿或发布文章

## Docker Compose 启动

```bash
cp .env.example .env
# 必须修改 .env 中的数据库密码、ADMIN_PASSWORD 和 AUTH_SECRET
docker compose up -d --build
```

打开 <http://localhost:18080>，API 文档位于 <http://localhost:18080/api/docs>。

如需使用其他端口：

```bash
BLOG_PORT=9000 docker compose up -d --build
```

首次启动时，后端会等待 MySQL 健康检查通过，自动执行 Alembic 数据库迁移，并在空库中写入初始文章和评论。MySQL 数据保存在 `mysql_data` Docker volume 中，因此普通重启或 `docker compose down` 不会清空内容。

管理员登录页不在公共导航中展示，需要直接访问 `/admin/login`。管理员账号由 `.env` 中的 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 初始化，默认账号名为 `baize`；首次初始化后可在“后台 → 站点设置 → 登录密码”中修改密码。未登录用户不能创建、修改或读取草稿，公开页面只能看到已发布文章。

后台支持维护“关于我”资料、个人原则、技术栈、文章分类和标签。分类、标签均可新增和改名，只有没有关联文章的空分类或空标签允许删除。文章支持新建、编辑、保存草稿、发布和二次确认删除。

查看服务状态和日志：

```bash
docker compose ps
docker compose logs -f backend mysql
```

停止服务但保留数据：

```bash
docker compose down
```

只有在明确需要重新初始化数据库时才执行 `docker compose down -v`；这会删除 `mysql_data` 中的全部文章、草稿和评论。

## 本地开发

后端：

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

本地开发默认使用 `sqlite:///./blog.db`，便于运行测试；生产/Compose 环境通过 `DATABASE_URL` 使用 MySQL。若要本地连接 MySQL，可先启动 Compose 的 mysql 服务，再导出与 `.env` 一致的连接串。

前端：

```bash
cd frontend
npm install
npm run dev
```

Vite 会把 `/api` 代理到 `http://localhost:8000`。
