import json
import mimetypes
import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.orm import Session

from .auth import authenticate, hash_password, require_admin, verify_password
from .database import get_db
from .models import AdminUser, Article, Category, Comment, SiteProfile, Tag, article_tags
from .schemas import ArticleWrite, CategoryWrite, CommentCreate, LoginRequest, PasswordChange, ProfileWrite, TagWrite
from .services import article_query, article_to_dict, calculate_read_time, get_or_create_category, get_or_create_tags, make_slug, set_status

app = FastAPI(title="Baize.dev Blog API", version="2.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(Path(__file__).resolve().parent.parent / "uploads")))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

ALLOWED_UPLOAD_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp", "image/avif",
    "application/pdf", "text/plain", "text/csv", "application/zip",
}
ALLOWED_UPLOAD_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".pdf", ".txt", ".csv", ".zip"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ok", "service": "blog-api", "database": "connected"}


@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    token = authenticate(db, payload.username, payload.password)
    if not token:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {"access_token": token, "token_type": "bearer", "user": {"username": payload.username, "role": "admin"}}


@app.get("/api/auth/me")
def me(admin=Depends(require_admin)):
    return {"username": admin["sub"], "role": admin["role"]}


@app.put("/api/auth/password")
def change_password(payload: PasswordChange, db: Session = Depends(get_db), admin=Depends(require_admin)):
    user = admin["user"]
    if not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="当前密码不正确")
    user.password_hash = hash_password(payload.new_password)
    user.password_changed_at = datetime.now()
    db.commit()
    return {"message": "密码已更新，请使用新密码重新登录"}


@app.post("/api/admin/uploads")
async def upload_resource(file: UploadFile = File(...), admin=Depends(require_admin)):
    """Store a small editor resource and return a public Markdown-ready URL."""
    original_name = Path(file.filename or "resource").name
    suffix = Path(original_name).suffix.lower()
    content_type = (file.content_type or mimetypes.guess_type(original_name)[0] or "").lower()
    if suffix not in ALLOWED_UPLOAD_EXTENSIONS or (content_type and content_type not in ALLOWED_UPLOAD_TYPES and content_type != "application/octet-stream"):
        raise HTTPException(status_code=415, detail="仅支持图片、PDF、文本、CSV 或 ZIP 文件")
    payload = await file.read(MAX_UPLOAD_SIZE + 1)
    if not payload:
        raise HTTPException(status_code=400, detail="不能上传空文件")
    if len(payload) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="文件不能超过 10MB")
    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", Path(original_name).stem).strip("-") or "resource"
    filename = f"{safe_stem}-{uuid.uuid4().hex[:10]}{suffix}"
    target = UPLOAD_DIR / filename
    target.write_bytes(payload)
    url = f"/uploads/{filename}"
    is_image = content_type.startswith("image/") or suffix in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}
    return {"name": original_name, "url": url, "markdown": f"![{original_name}]({url})" if is_image else f"[{original_name}]({url})", "content_type": content_type, "size": len(payload)}


def profile_to_dict(profile: SiteProfile):
    return {
        "name": profile.name, "initials": profile.initials, "title": profile.title,
        "hero_intro": profile.hero_intro, "hero_skills": json.loads(profile.hero_skills or "[]"),
        "writing_since_year": profile.writing_since_year, "views_baseline": profile.views_baseline,
        "bio": profile.bio, "story": profile.story, "location": profile.location,
        "email": profile.email, "github": profile.github,
        "principles": json.loads(profile.principles or "[]"), "stack": json.loads(profile.stack or "[]"),
    }


@app.get("/api/profile")
def get_profile(db: Session = Depends(get_db)):
    profile = db.scalar(select(SiteProfile).where(SiteProfile.id == 1))
    if not profile:
        raise HTTPException(404, "个人资料尚未配置")
    return profile_to_dict(profile)


@app.put("/api/admin/profile")
def update_profile(payload: ProfileWrite, db: Session = Depends(get_db), admin=Depends(require_admin)):
    profile = db.scalar(select(SiteProfile).where(SiteProfile.id == 1))
    if not profile:
        profile = SiteProfile(id=1)
        db.add(profile)
    for key in ("name", "initials", "title", "hero_intro", "writing_since_year", "views_baseline", "bio", "story", "location", "email", "github"):
        setattr(profile, key, getattr(payload, key))
    profile.hero_skills = json.dumps(payload.hero_skills, ensure_ascii=False)
    profile.principles = json.dumps(payload.principles, ensure_ascii=False)
    profile.stack = json.dumps(payload.stack, ensure_ascii=False)
    db.commit(); db.refresh(profile)
    return profile_to_dict(profile)


@app.get("/api/stats")
def get_site_stats(db: Session = Depends(get_db)):
    profile = db.scalar(select(SiteProfile).where(SiteProfile.id == 1))
    published_posts = db.scalar(select(func.count(Article.id)).where(Article.status == "published")) or 0
    actual_views = db.scalar(select(func.coalesce(func.sum(Article.views), 0)).where(Article.status == "published")) or 0
    writing_since_year = profile.writing_since_year if profile else datetime.now().year
    views_baseline = profile.views_baseline if profile else 0
    return {
        "published_posts": published_posts,
        "actual_views": actual_views,
        "views_baseline": views_baseline,
        "total_views": actual_views + views_baseline,
        "writing_since_year": writing_since_year,
        "writing_years": max(1, datetime.now().year - writing_since_year),
    }

@app.get("/api/posts")
def list_posts(page: int = Query(1, ge=1), page_size: int = Query(6, ge=1, le=100), tag: str | None = None,
               category: str | None = None, query: str | None = None,
               article_status: str = Query("published", alias="status"), db: Session = Depends(get_db)):
    if article_status != "published":
        raise HTTPException(status_code=401, detail="草稿仅管理员可见")
    stmt = article_query().where(Article.status == article_status)
    count_stmt = select(func.count(func.distinct(Article.id))).where(Article.status == article_status)
    if tag:
        stmt = stmt.join(Article.tags).where(Tag.name == tag)
        count_stmt = count_stmt.join(Article.tags).where(Tag.name == tag)
    if category:
        stmt = stmt.join(Article.category).where(Category.name == category)
        count_stmt = count_stmt.join(Article.category).where(Category.name == category)
    if query:
        condition = or_(Article.title.ilike(f"%{query}%"), Article.excerpt.ilike(f"%{query}%"), Article.content.ilike(f"%{query}%"))
        stmt, count_stmt = stmt.where(condition), count_stmt.where(condition)
    total = db.scalar(count_stmt) or 0
    articles = db.scalars(stmt.order_by(Article.created_at.desc(), Article.id.desc()).offset((page-1)*page_size).limit(page_size)).unique().all()
    return {"items": [article_to_dict(item) for item in articles], "total": total, "page": page, "page_size": page_size}

@app.get("/api/admin/posts")
def list_admin_posts(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    query: str | None = None,
    article_status: str = Query("all", alias="status"),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    if article_status not in {"all", "draft", "published"}:
        raise HTTPException(status_code=422, detail="无效的文章状态")

    stmt = article_query()
    count_stmt = select(func.count(Article.id))
    if article_status != "all":
        stmt = stmt.where(Article.status == article_status)
        count_stmt = count_stmt.where(Article.status == article_status)
    if query and query.strip():
        keyword = f"%{query.strip()}%"
        condition = or_(Article.title.ilike(keyword), Article.excerpt.ilike(keyword), Article.content.ilike(keyword))
        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    total = db.scalar(count_stmt) or 0
    articles = db.scalars(
        stmt.order_by(Article.updated_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).unique().all()
    all_total = db.scalar(select(func.count(Article.id))) or 0
    published_total = db.scalar(select(func.count(Article.id)).where(Article.status == "published")) or 0
    draft_total = db.scalar(select(func.count(Article.id)).where(Article.status == "draft")) or 0
    return {
        "items": [article_to_dict(item) for item in articles],
        "total": total,
        "page": page,
        "page_size": page_size,
        "all_total": all_total,
        "published_total": published_total,
        "draft_total": draft_total,
    }


@app.get("/api/posts/{slug}")
def get_post(slug: str, db: Session = Depends(get_db)):
    result = db.execute(
        update(Article)
        .where(Article.slug == slug, Article.status == "published")
        .values(views=Article.views + 1)
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(404, "文章不存在")
    db.commit()
    article = db.scalar(article_query().where(Article.slug == slug, Article.status == "published"))
    return article_to_dict(article)


@app.get("/api/admin/posts/{slug}")
def get_admin_post(slug: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    article = db.scalar(article_query().where(Article.slug == slug))
    if not article:
        raise HTTPException(404, "文章不存在")
    return article_to_dict(article)


@app.post("/api/posts/{slug}/like")
def like_post(slug: str, db: Session = Depends(get_db)):
    result = db.execute(
        update(Article)
        .where(Article.slug == slug, Article.status == "published")
        .values(likes=Article.likes + 1)
    )
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(404, "文章不存在")
    db.commit()
    likes = db.scalar(select(Article.likes).where(Article.slug == slug)) or 0
    return {"id": slug, "likes": likes}


@app.delete("/api/admin/posts/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_admin_post(slug: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    article = db.scalar(article_query().where(Article.slug == slug))
    if not article:
        raise HTTPException(404, "文章不存在")
    db.delete(article)
    db.commit()


@app.post("/api/posts", status_code=status.HTTP_201_CREATED)
def create_post(payload: ArticleWrite, db: Session = Depends(get_db), admin=Depends(require_admin)):
    slug = make_slug(payload.title)
    while db.scalar(select(Article.id).where(Article.slug == slug)):
        slug = f"{slug}-new"
    article = Article(slug=slug, title=payload.title, excerpt=payload.excerpt or payload.content.replace("#", "")[:180],
        content=payload.content, category=get_or_create_category(db, payload.category), tags=get_or_create_tags(db, payload.tags),
        read_time=calculate_read_time(payload.content))
    set_status(article, payload.status)
    db.add(article); db.commit(); db.refresh(article)
    return article_to_dict(db.scalar(article_query().where(Article.id == article.id)))

@app.put("/api/posts/{slug}")
def update_post(slug: str, payload: ArticleWrite, db: Session = Depends(get_db), admin=Depends(require_admin)):
    article = db.scalar(article_query().where(Article.slug == slug))
    if not article:
        raise HTTPException(404, "文章不存在")
    article.title, article.content, article.excerpt = payload.title, payload.content, payload.excerpt
    article.read_time = calculate_read_time(payload.content)
    article.category, article.tags = get_or_create_category(db, payload.category), get_or_create_tags(db, payload.tags)
    set_status(article, payload.status); db.commit(); db.refresh(article)
    return article_to_dict(article)

@app.get("/api/tags")
def list_tags(db: Session = Depends(get_db)):
    published_count = func.count(Article.id)
    rows = db.execute(
        select(Tag.name, Tag.slug, published_count)
        .select_from(Tag)
        .outerjoin(article_tags, article_tags.c.tag_id == Tag.id)
        .outerjoin(
            Article,
            and_(Article.id == article_tags.c.article_id, Article.status == "published"),
        )
        .group_by(Tag.id, Tag.name, Tag.slug)
        .order_by(published_count.desc(), Tag.name.asc())
    ).all()
    return [{"name": name, "slug": slug, "count": count} for name, slug, count in rows]


@app.get("/api/admin/tags")
def list_admin_tags(db: Session = Depends(get_db), admin=Depends(require_admin)):
    rows = db.execute(select(Tag, func.count(Article.id)).outerjoin(Tag.articles).group_by(Tag.id).order_by(Tag.name.asc())).all()
    return [{"id": tag.id, "name": tag.name, "slug": tag.slug, "count": count} for tag, count in rows]


@app.post("/api/admin/tags", status_code=status.HTTP_201_CREATED)
def create_tag(payload: TagWrite, db: Session = Depends(get_db), admin=Depends(require_admin)):
    name = payload.name.strip()
    if db.scalar(select(Tag).where(Tag.name == name)):
        raise HTTPException(409, "标签已存在")
    tag = Tag(name=name, slug=make_slug(name))
    db.add(tag); db.commit(); db.refresh(tag)
    return {"id": tag.id, "name": tag.name, "slug": tag.slug, "count": 0}


@app.put("/api/admin/tags/{slug}")
def update_tag(slug: str, payload: TagWrite, db: Session = Depends(get_db), admin=Depends(require_admin)):
    tag = db.scalar(select(Tag).where(Tag.slug == slug))
    if not tag:
        raise HTTPException(404, "标签不存在")
    name = payload.name.strip()
    duplicate = db.scalar(select(Tag).where(Tag.name == name, Tag.id != tag.id))
    if duplicate:
        raise HTTPException(409, "标签已存在")
    tag.name = name; tag.slug = make_slug(name)
    db.commit(); db.refresh(tag)
    return {"id": tag.id, "name": tag.name, "slug": tag.slug}


@app.delete("/api/admin/tags/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(slug: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    tag = db.scalar(select(Tag).where(Tag.slug == slug))
    if not tag:
        raise HTTPException(404, "标签不存在")
    count = db.scalar(select(func.count(Article.id)).select_from(Tag).join(Tag.articles).where(Tag.id == tag.id)) or 0
    if count:
        raise HTTPException(409, f"该标签仍被 {count} 篇文章使用，不能删除")
    db.delete(tag); db.commit()

@app.get("/api/categories")
def list_categories(db: Session = Depends(get_db)):
    published_count = func.count(Article.id)
    rows = db.execute(
        select(Category.name, Category.slug, published_count)
        .select_from(Category)
        .outerjoin(
            Article,
            and_(Article.category_id == Category.id, Article.status == "published"),
        )
        .group_by(Category.id, Category.name, Category.slug)
        .order_by(published_count.desc(), Category.name.asc())
    ).all()
    return [{"name": name, "slug": slug, "count": count} for name, slug, count in rows]


@app.get("/api/admin/categories")
def list_admin_categories(db: Session = Depends(get_db), admin=Depends(require_admin)):
    rows = db.execute(select(Category, func.count(Article.id)).outerjoin(Category.articles).group_by(Category.id).order_by(Category.name.asc())).all()
    return [{"id": category.id, "name": category.name, "slug": category.slug, "count": count} for category, count in rows]


@app.post("/api/admin/categories", status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryWrite, db: Session = Depends(get_db), admin=Depends(require_admin)):
    if db.scalar(select(Category).where(Category.name == payload.name.strip())):
        raise HTTPException(409, "分类已存在")
    category = Category(name=payload.name.strip(), slug=make_slug(payload.name))
    db.add(category); db.commit(); db.refresh(category)
    return {"id": category.id, "name": category.name, "slug": category.slug, "count": 0}


@app.put("/api/admin/categories/{slug}")
def update_category(slug: str, payload: CategoryWrite, db: Session = Depends(get_db), admin=Depends(require_admin)):
    category = db.scalar(select(Category).where(Category.slug == slug))
    if not category:
        raise HTTPException(404, "分类不存在")
    duplicate = db.scalar(select(Category).where(Category.name == payload.name.strip(), Category.id != category.id))
    if duplicate:
        raise HTTPException(409, "分类已存在")
    category.name = payload.name.strip(); category.slug = make_slug(payload.name)
    db.commit(); db.refresh(category)
    return {"id": category.id, "name": category.name, "slug": category.slug}


@app.delete("/api/admin/categories/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(slug: str, db: Session = Depends(get_db), admin=Depends(require_admin)):
    category = db.scalar(select(Category).where(Category.slug == slug))
    if not category:
        raise HTTPException(404, "分类不存在")
    count = db.scalar(select(func.count(Article.id)).where(Article.category_id == category.id)) or 0
    if count:
        raise HTTPException(409, f"该分类仍有 {count} 篇文章，不能删除")
    db.delete(category); db.commit()

@app.get("/api/posts/{slug}/comments")
def list_comments(slug: str, db: Session = Depends(get_db)):
    comments = db.scalars(select(Comment).join(Comment.article).where(Article.slug==slug, Comment.status=="approved").order_by(Comment.created_at.desc())).all()
    return [{"id": item.id, "name": item.name, "content": item.content, "created_at": item.created_at.strftime("%Y-%m-%d %H:%M")} for item in comments]

@app.post("/api/posts/{slug}/comments", status_code=status.HTTP_201_CREATED)
def create_comment(slug: str, payload: CommentCreate, db: Session = Depends(get_db)):
    article = db.scalar(select(Article).where(Article.slug==slug))
    if not article:
        raise HTTPException(404, "文章不存在")
    comment = Comment(article=article, name=payload.name, content=payload.content)
    db.add(comment); db.commit(); db.refresh(comment)
    return {"id": comment.id, "name": comment.name, "content": comment.content, "created_at": comment.created_at.strftime("%Y-%m-%d %H:%M")}
