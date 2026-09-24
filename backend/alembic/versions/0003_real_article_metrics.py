"""replace demo article metrics with real values"""
from math import ceil
import re

from alembic import op
import sqlalchemy as sa


revision = "0003_real_article_metrics"
down_revision = "0002_admin_profile"
branch_labels = None
depends_on = None


SEED_SLUGS = {
    "react-server-components", "typescript-patterns", "ai-coding-workflow",
    "web-performance", "node-observability", "css-design-system",
    "postgres-index", "docker-small-image", "micro-frontend",
    "go-concurrency", "api-design", "testing-pyramid",
}


def calculate_read_time(content):
    plain_text = re.sub(r"```[\s\S]*?```", " ", content or "")
    plain_text = re.sub(r"[#>*_`\[\](){}|~-]", " ", plain_text)
    chinese_characters = len(re.findall(r"[\u4e00-\u9fff]", plain_text))
    latin_words = len(re.findall(r"[A-Za-z0-9]+(?:['.-][A-Za-z0-9]+)*", plain_text))
    return f"{max(1, ceil(chinese_characters / 400 + latin_words / 200))} 分钟"


def upgrade():
    connection = op.get_bind()
    articles = sa.table(
        "articles",
        sa.column("id", sa.Integer),
        sa.column("slug", sa.String),
        sa.column("content", sa.Text),
        sa.column("views", sa.Integer),
        sa.column("read_time", sa.String),
        sa.column("created_at", sa.DateTime),
        sa.column("published_at", sa.DateTime),
    )
    rows = connection.execute(sa.select(
        articles.c.id,
        articles.c.slug,
        articles.c.content,
        articles.c.published_at,
    )).mappings().all()
    for row in rows:
        values = {"read_time": calculate_read_time(row["content"])}
        if row["slug"] in SEED_SLUGS:
            values["views"] = 0
            if row["published_at"] is not None:
                values["created_at"] = row["published_at"]
        connection.execute(sa.update(articles).where(articles.c.id == row["id"]).values(**values))


def downgrade():
    pass
