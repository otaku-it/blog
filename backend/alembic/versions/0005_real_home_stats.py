"""add configurable real home statistics"""
from alembic import op
import sqlalchemy as sa


revision = "0005_real_home_stats"
down_revision = "0004_home_hero_settings"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("site_profile", sa.Column("writing_since_year", sa.Integer(), nullable=False, server_default="2021"))
    op.add_column("site_profile", sa.Column("views_baseline", sa.Integer(), nullable=False, server_default="0"))
    op.alter_column("site_profile", "writing_since_year", existing_type=sa.Integer(), server_default=None, existing_nullable=False)
    op.alter_column("site_profile", "views_baseline", existing_type=sa.Integer(), server_default=None, existing_nullable=False)


def downgrade():
    op.drop_column("site_profile", "views_baseline")
    op.drop_column("site_profile", "writing_since_year")
