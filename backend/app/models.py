from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

article_tags = Table(
    "article_tags", Base.metadata,
    Column("article_id", ForeignKey("articles.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    articles: Mapped[list["Article"]] = relationship(back_populates="category")

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    articles: Mapped[list["Article"]] = relationship(secondary=article_tags, back_populates="tags")

class Article(Base):
    __tablename__ = "articles"
    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(160), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(160), index=True)
    excerpt: Mapped[str] = mapped_column(String(500), default="")
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)
    read_time: Mapped[str] = mapped_column(String(30), default="5 分钟")
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    published_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    category: Mapped[Category | None] = relationship(back_populates="articles")
    tags: Mapped[list[Tag]] = relationship(secondary=article_tags, back_populates="articles")
    comments: Mapped[list["Comment"]] = relationship(back_populates="article", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(String(1000))
    status: Mapped[str] = mapped_column(String(20), default="approved", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    article: Mapped[Article] = relationship(back_populates="comments")


class AdminUser(Base):
    __tablename__ = "admin_users"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    password_changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class SiteProfile(Base):
    __tablename__ = "site_profile"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), default="白泽")
    initials: Mapped[str] = mapped_column(String(20), default="BZ")
    title: Mapped[str] = mapped_column(String(160), default="全栈工程师与技术写作者")
    hero_intro: Mapped[str] = mapped_column(Text, default="你好，我是白泽，全栈工程师与技术写作者。这里分享前端架构、AI 编程、工程效率，以及值得被认真记录的技术思考。")
    hero_skills: Mapped[str] = mapped_column(Text, default='["React", "Next.js", "AI"]')
    writing_since_year: Mapped[int] = mapped_column(Integer, default=2021)
    views_baseline: Mapped[int] = mapped_column(Integer, default=0)
    bio: Mapped[str] = mapped_column(Text, default="")
    story: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String(120), default="中国 · 上海")
    email: Mapped[str] = mapped_column(String(160), default="hello@example.com")
    github: Mapped[str] = mapped_column(String(255), default="https://github.com")
    principles: Mapped[str] = mapped_column(Text, default="[]")
    stack: Mapped[str] = mapped_column(Text, default="[]")
