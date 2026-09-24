from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    name: str = Field(default="访客", min_length=1, max_length=30)
    content: str = Field(min_length=1, max_length=500)


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=1, max_length=200)


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)


class ProfileWrite(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    initials: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=1, max_length=160)
    hero_intro: str = Field(default="", max_length=1000)
    hero_skills: list[str] = Field(default_factory=list, max_length=8)
    writing_since_year: int = Field(default=2021, ge=1970, le=2100)
    views_baseline: int = Field(default=0, ge=0, le=2_000_000_000)
    bio: str = Field(default="", max_length=3000)
    story: str = Field(default="", max_length=6000)
    location: str = Field(default="", max_length=120)
    email: str = Field(default="", max_length=160)
    github: str = Field(default="", max_length=255)
    principles: list[dict] = Field(default_factory=list, max_length=8)
    stack: list[dict] = Field(default_factory=list, max_length=8)


class CategoryWrite(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagWrite(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class ArticleWrite(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    content: str = Field(min_length=1)
    tags: list[str] = Field(default_factory=list, max_length=5)
    excerpt: str = Field(default="", max_length=500)
    category: str = Field(default="技术随笔", max_length=50)
    status: str = Field(default="draft", pattern="^(draft|published)$")
