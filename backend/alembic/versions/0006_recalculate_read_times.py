"""recalculate cached reading times from full article content"""
from math import ceil
import re

from alembic import op
import sqlalchemy as sa


revision = "0006_recalculate_read_times"
down_revision = "0005_real_home_stats"
branch_labels = None
depends_on = None


def estimate(content):
    plain_text = re.sub(r"```[^\n]*\n?", " ", content or "")
    plain_text = re.sub(r"[#>*_`\[\](){}|~-]", " ", plain_text)
    chinese = len(re.findall(r"[\u4e00-\u9fff]", plain_text))
    latin = len(re.findall(r"[A-Za-z0-9]+(?:['.-][A-Za-z0-9]+)*", plain_text))
    return f"{max(1, ceil(chinese / 300 + latin / 200))} 分钟"


def upgrade():
    connection = op.get_bind()
    articles = sa.table(
        "articles",
        sa.column("id", sa.Integer),
        sa.column("content", sa.Text),
        sa.column("read_time", sa.String),
    )
    rows = connection.execute(sa.select(articles.c.id, articles.c.content)).mappings().all()
    for row in rows:
        connection.execute(sa.update(articles).where(articles.c.id == row["id"]).values(read_time=estimate(row["content"])))


def downgrade():
    pass
