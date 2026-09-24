"""admin users and editable site profile"""
from alembic import op
import sqlalchemy as sa

revision = "0002_admin_profile"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("admin_users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("username", sa.String(50), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("password_changed_at", sa.DateTime(), nullable=False), sa.UniqueConstraint("username"))
    op.create_index("ix_admin_users_username", "admin_users", ["username"])
    op.create_table("site_profile", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(80), nullable=False), sa.Column("initials", sa.String(20), nullable=False), sa.Column("title", sa.String(160), nullable=False), sa.Column("bio", sa.Text(), nullable=False), sa.Column("story", sa.Text(), nullable=False), sa.Column("location", sa.String(120), nullable=False), sa.Column("email", sa.String(160), nullable=False), sa.Column("github", sa.String(255), nullable=False), sa.Column("principles", sa.Text(), nullable=False), sa.Column("stack", sa.Text(), nullable=False))


def downgrade():
    op.drop_table("site_profile")
    op.drop_index("ix_admin_users_username", table_name="admin_users")
    op.drop_table("admin_users")
