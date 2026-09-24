import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

def get_database_url():
    configured = os.getenv("DATABASE_URL", "").strip()
    if configured:
        return configured
    if os.getenv("MYSQL_HOST"):
        from urllib.parse import quote_plus
        host = os.getenv("MYSQL_HOST", "host.docker.internal")
        port = os.getenv("MYSQL_PORT", "3308")
        database = os.getenv("MYSQL_DATABASE", "blog")
        user = quote_plus(os.getenv("MYSQL_USER", "root"))
        password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
        return f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4"
    return "sqlite:///./blog.db"


DATABASE_URL = get_database_url()
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, pool_pre_ping=True, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
