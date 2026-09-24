import json
from datetime import datetime
from sqlalchemy import func, select
from .auth import ADMIN_PASSWORD, ADMIN_USERNAME, hash_password
from .data import COMMENTS, POSTS
from .database import SessionLocal
from .models import AdminUser, Article, Comment, SiteProfile
from .services import calculate_read_time, get_or_create_category, get_or_create_tags

def seed():
    with SessionLocal() as db:
        if not db.scalar(select(AdminUser.id).limit(1)):
            db.add(AdminUser(username=ADMIN_USERNAME, password_hash=hash_password(ADMIN_PASSWORD)))
        if not db.scalar(select(SiteProfile.id).limit(1)):
            db.add(SiteProfile(
                name="白泽", initials="BZ", title="全栈工程师与技术写作者",
                hero_intro="你好，我是白泽，全栈工程师与技术写作者。这里分享前端架构、AI 编程、工程效率，以及值得被认真记录的技术思考。",
                hero_skills=json.dumps(["React", "Next.js", "AI"], ensure_ascii=False),
                writing_since_year=2021, views_baseline=0,
                bio="一名有产品思维的全栈工程师，也是一个长期主义的技术写作者。",
                story="过去 8 年，我参与过从 0 到 1 的创业产品，也维护过面向大量用户的 Web 系统。目前专注于开发者工具与 AI 应用方向。\n\n我喜欢研究复杂系统背后的简单原则，也享受把模糊想法变成清晰、可用的产品。",
                location="中国 · 上海", email="hello@example.com", github="https://github.com",
                principles=json.dumps([
                    {"title": "清晰胜过聪明", "description": "让代码、界面与表达尽可能容易理解。"},
                    {"title": "系统胜过意志", "description": "用可重复的流程解决问题。"},
                    {"title": "交付胜过想象", "description": "真实反馈比会议室里的完美设想更有价值。"},
                ], ensure_ascii=False),
                stack=json.dumps([
                    {"group": "前端", "items": ["Vue", "TypeScript", "Tailwind CSS"]},
                    {"group": "后端", "items": ["Python", "FastAPI", "MySQL"]},
                    {"group": "工程", "items": ["Docker", "CI/CD", "可观测性"]},
                ], ensure_ascii=False),
            ))
        if (db.scalar(select(func.count(Article.id))) or 0) == 0:
            articles = {}
            for item in POSTS:
                created_at = datetime.fromisoformat(item["date"])
                article = Article(slug=item["id"], title=item["title"], excerpt=item["excerpt"], content=item["content"],
                    status="published", views=0, read_time=calculate_read_time(item["content"]),
                    category=get_or_create_category(db, item["category"]), tags=get_or_create_tags(db, item["tags"]),
                    created_at=created_at, updated_at=created_at, published_at=created_at)
                db.add(article); db.flush(); articles[item["id"]] = article
            for slug, items in COMMENTS.items():
                for item in items:
                    db.add(Comment(article=articles[slug], name=item["name"], content=item["content"]))
        db.commit()

if __name__ == "__main__":
    seed()
