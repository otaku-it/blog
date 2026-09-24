import os
import subprocess
import sys
import time
from urllib.parse import quote_plus, urlsplit

import pymysql
from sqlalchemy import create_engine, text


def ensure_mysql_database() -> None:
    database = os.getenv("MYSQL_DATABASE", "blog")
    if not database or "`" in database or len(database) > 64:
        raise RuntimeError("MYSQL_DATABASE is invalid")
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "host.docker.internal"),
        port=int(os.getenv("MYSQL_PORT", "3308")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        connect_timeout=5,
        charset="utf8mb4",
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{database}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci"
            )
        connection.commit()
    finally:
        connection.close()


def database_url() -> tuple[str, bool]:
    configured = os.getenv("DATABASE_URL", "").strip()
    if configured:
        return configured, False
    host = os.getenv("MYSQL_HOST", "host.docker.internal")
    port = os.getenv("MYSQL_PORT", "3308")
    database = os.getenv("MYSQL_DATABASE", "blog")
    user = quote_plus(os.getenv("MYSQL_USER", "root"))
    password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4", True


url, manages_database = database_url()
os.environ["DATABASE_URL"] = url
parsed = urlsplit(url.replace("mysql+pymysql://", "http://", 1))
safe_target = f"{parsed.hostname}:{parsed.port or 3306}/{parsed.path.lstrip('/')}"
retries = max(1, int(os.getenv("DB_CONNECT_RETRIES", "30")))
interval = max(1, int(os.getenv("DB_CONNECT_INTERVAL", "2")))

for attempt in range(1, retries + 1):
    try:
        if manages_database:
            ensure_mysql_database()
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        engine.dispose()
        print(f"Database connected: {safe_target}", flush=True)
        break
    except Exception as exc:
        print(f"Waiting for existing MySQL ({attempt}/{retries}) at {safe_target}: {exc}", flush=True)
        if attempt == retries:
            print("Cannot connect to existing MySQL. Check MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER and MYSQL_PASSWORD.", flush=True)
            sys.exit(1)
        time.sleep(interval)

subprocess.run(["alembic", "upgrade", "head"], check=True)
subprocess.run([sys.executable, "-m", "app.seed"], check=True)
os.execvp("uvicorn", ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"])
