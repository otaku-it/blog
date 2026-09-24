"""add editable home hero content"""
from alembic import op
import sqlalchemy as sa


revision = "0004_home_hero_settings"
down_revision = "0003_real_article_metrics"
branch_labels = None
depends_on = None


DEFAULT_INTRO = "你好，我是白泽，全栈工程师与技术写作者。这里分享前端架构、AI 编程、工程效率，以及值得被认真记录的技术思考。"
DEFAULT_SKILLS = '["React", "Next.js", "AI"]'


def upgrade():
    op.add_column("site_profile", sa.Column("hero_intro", sa.Text(), nullable=True))
    op.add_column("site_profile", sa.Column("hero_skills", sa.Text(), nullable=True))
    profile = sa.table(
        "site_profile",
        sa.column("hero_intro", sa.Text),
        sa.column("hero_skills", sa.Text),
    )
    op.execute(sa.update(profile).values(hero_intro=DEFAULT_INTRO, hero_skills=DEFAULT_SKILLS))
    op.alter_column("site_profile", "hero_intro", existing_type=sa.Text(), nullable=False, existing_nullable=True)
    op.alter_column("site_profile", "hero_skills", existing_type=sa.Text(), nullable=False, existing_nullable=True)


def downgrade():
    op.drop_column("site_profile", "hero_skills")
    op.drop_column("site_profile", "hero_intro")
