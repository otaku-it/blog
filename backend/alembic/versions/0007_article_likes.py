"""add persistent article likes"""
from alembic import op
import sqlalchemy as sa


revision = "0007_article_likes"
down_revision = "0006_recalculate_read_times"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("articles", sa.Column("likes", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("articles", "likes", server_default=None, existing_type=sa.Integer(), existing_nullable=False)


def downgrade():
    op.drop_column("articles", "likes")
