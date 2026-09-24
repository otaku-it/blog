import re
import uuid
from math import ceil
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from .models import Article, Category, Tag

def make_slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or f"article-{uuid.uuid4().hex[:10]}"

def reading_metrics(content: str) -> tuple[int, int]:
    """Return readable units and estimated minutes from the full Markdown body."""
    plain_text = re.sub(r"```[^\n]*\n?", " ", content or "")
    plain_text = re.sub(r"[#>*_`\[\](){}|~-]", " ", plain_text)
    chinese_characters = len(re.findall(r"[\u4e00-\u9fff]", plain_text))
    latin_words = len(re.findall(r"[A-Za-z0-9]+(?:['.-][A-Za-z0-9]+)*", plain_text))
    word_count = chinese_characters + latin_words
    minutes = max(1, ceil(chinese_characters / 300 + latin_words / 200))
    return word_count, minutes

def calculate_read_time(content: str) -> str:
    _, minutes = reading_metrics(content)
    return f"{minutes} 分钟"

def get_or_create_category(db: Session, name: str | None):
    if not name:
        return None
    category = db.scalar(select(Category).where(Category.name == name))
    if not category:
        category = Category(name=name, slug=make_slug(name)); db.add(category); db.flush()
    return category

def get_or_create_tags(db: Session, names: list[str]):
    tags = []
    for name in dict.fromkeys(item.strip() for item in names if item.strip()):
        tag = db.scalar(select(Tag).where(Tag.name == name))
        if not tag:
            tag = Tag(name=name, slug=make_slug(name)); db.add(tag); db.flush()
        tags.append(tag)
    return tags

def article_query():
    return select(Article).options(selectinload(Article.tags), selectinload(Article.category))

def article_to_dict(article: Article):
    word_count, minutes = reading_metrics(article.content)
    return {"id": article.slug, "title": article.title, "excerpt": article.excerpt, "content": article.content,
            "status": article.status, "date": article.created_at.date().isoformat(),
            "category": article.category.name if article.category else "未分类", "tags": [tag.name for tag in article.tags],
            "views": article.views, "likes": article.likes, "read_time": f"{minutes} 分钟", "word_count": word_count, "created_at": article.created_at.isoformat(),
            "updated_at": article.updated_at.isoformat()}

def set_status(article: Article, status: str):
    article.status = status
    if status == "published" and article.published_at is None:
        article.published_at = datetime.now()
