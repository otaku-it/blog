"""initial blog schema"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("categories", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(50), nullable=False), sa.Column("slug", sa.String(80), nullable=False), sa.UniqueConstraint("name"), sa.UniqueConstraint("slug"))
    op.create_index("ix_categories_name", "categories", ["name"]); op.create_index("ix_categories_slug", "categories", ["slug"])
    op.create_table("tags", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(50), nullable=False), sa.Column("slug", sa.String(80), nullable=False), sa.UniqueConstraint("name"), sa.UniqueConstraint("slug"))
    op.create_index("ix_tags_name", "tags", ["name"]); op.create_index("ix_tags_slug", "tags", ["slug"])
    op.create_table("articles", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("slug", sa.String(160), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("excerpt", sa.String(500), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("views", sa.Integer(), nullable=False), sa.Column("read_time", sa.String(30), nullable=False), sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False), sa.Column("published_at", sa.DateTime(), nullable=True), sa.UniqueConstraint("slug"))
    for name, cols in [("ix_articles_slug", ["slug"]), ("ix_articles_title", ["title"]), ("ix_articles_status", ["status"]), ("ix_articles_published_at", ["published_at"])]: op.create_index(name, "articles", cols)
    op.create_table("article_tags", sa.Column("article_id", sa.Integer(), sa.ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True), sa.Column("tag_id", sa.Integer(), sa.ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True))
    op.create_table("comments", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("article_id", sa.Integer(), sa.ForeignKey("articles.id", ondelete="CASCADE"), nullable=False), sa.Column("name", sa.String(50), nullable=False), sa.Column("content", sa.String(1000), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_comments_article_id", "comments", ["article_id"]); op.create_index("ix_comments_status", "comments", ["status"])

def downgrade():
    op.drop_table("comments"); op.drop_table("article_tags"); op.drop_table("articles"); op.drop_table("tags"); op.drop_table("categories")
