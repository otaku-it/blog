from pathlib import Path

from fastapi.testclient import TestClient

from app.main import UPLOAD_DIR, app
from app.services import calculate_read_time

client = TestClient(app)


def test_health():
    assert client.get("/api/health").json()["status"] == "ok"


def test_posts_support_pagination_and_filter():
    response = client.get("/api/posts", params={"page": 1, "page_size": 2, "tag": "架构"})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) <= 2
    assert all("架构" in post["tags"] for post in payload["items"])
    created_times = [post["created_at"] for post in payload["items"]]
    assert created_times == sorted(created_times, reverse=True)


def test_post_detail_and_comment():
    first_view = client.get("/api/posts/react-server-components")
    second_view = client.get("/api/posts/react-server-components")
    assert first_view.status_code == 200
    assert second_view.json()["views"] == first_view.json()["views"] + 1
    response = client.post(
        "/api/posts/react-server-components/comments",
        json={"name": "Tester", "content": "很清晰的文章"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Tester"


def test_article_like_is_persisted():
    before = client.get("/api/posts/react-server-components").json()["likes"]
    first = client.post("/api/posts/react-server-components/like")
    second = client.post("/api/posts/react-server-components/like")
    assert first.status_code == 200
    assert first.json()["likes"] == before + 1
    assert second.json()["likes"] == before + 2
    assert client.get("/api/posts/react-server-components").json()["likes"] == before + 2


def test_admin_can_upload_editor_image():
    token = client.post("/api/auth/login", json={"username": "baize", "password": "change-me-now"}).json()["access_token"]
    response = client.post(
        "/api/admin/uploads",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("example.png", b"fake-png-content", "image/png")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["url"].startswith("/uploads/")
    assert payload["markdown"].startswith("![example.png](/uploads/")
    uploaded = UPLOAD_DIR / Path(payload["url"]).name
    assert uploaded.exists()
    public_file = client.get(payload["url"])
    assert public_file.status_code == 200
    assert public_file.content == b"fake-png-content"
    uploaded.unlink()


def test_read_time_is_calculated_from_article_content():
    assert calculate_read_time("很短的正文") == "1 分钟"
    assert calculate_read_time("技术内容" * 401) == "6 分钟"


def test_admin_publish_requires_login():
    payload = {"title": "未授权文章", "content": "正文", "tags": [], "category": "测试", "status": "published"}
    assert client.post("/api/posts", json=payload).status_code == 401
    token = client.post("/api/auth/login", json={"username": "baize", "password": "change-me-now"}).json()["access_token"]
    response = client.post("/api/posts", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    slug = response.json()["id"]
    assert client.delete(f"/api/admin/posts/{slug}").status_code == 401
    assert client.delete(f"/api/admin/posts/{slug}", headers={"Authorization": f"Bearer {token}"}).status_code == 204
    assert client.get(f"/api/admin/posts/{slug}", headers={"Authorization": f"Bearer {token}"}).status_code == 404


def test_admin_posts_support_server_pagination_status_and_search():
    token = client.post("/api/auth/login", json={"username": "baize", "password": "change-me-now"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    first_page = client.get("/api/admin/posts", params={"page": 1, "page_size": 5}, headers=headers)
    assert first_page.status_code == 200
    payload = first_page.json()
    assert len(payload["items"]) <= 5
    assert payload["page"] == 1
    assert payload["page_size"] == 5
    assert payload["all_total"] == payload["published_total"] + payload["draft_total"]

    drafts = client.get("/api/admin/posts", params={"status": "draft", "page_size": 100}, headers=headers).json()
    assert all(post["status"] == "draft" for post in drafts["items"])
    published = client.get("/api/admin/posts", params={"status": "published", "page_size": 100}, headers=headers).json()
    assert all(post["status"] == "published" for post in published["items"])

    searched = client.get("/api/admin/posts", params={"query": "React", "page_size": 100}, headers=headers)
    assert searched.status_code == 200
    assert all("react" in f'{post["title"]} {post["excerpt"]} {post["content"]}'.lower() for post in searched.json()["items"])
    assert client.get("/api/admin/posts").status_code == 401


def test_profile_and_categories_are_admin_managed():
    profile = client.get("/api/profile")
    assert profile.status_code == 200
    assert profile.json()["name"] == "白泽"
    token = client.post("/api/auth/login", json={"username": "baize", "password": "change-me-now"}).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    profile_payload = profile.json()
    profile_payload["hero_intro"] = "可后台维护的首页首屏介绍"
    profile_payload["hero_skills"] = ["Vue", "FastAPI", "AI"]
    profile_payload["writing_since_year"] = 2020
    profile_payload["views_baseline"] = 1200
    profile_payload["stack"].append({"group": "AI", "items": ["Codex", "Claude"]})
    updated_profile = client.put("/api/admin/profile", headers=headers, json=profile_payload)
    assert updated_profile.status_code == 200
    assert updated_profile.json()["hero_intro"] == "可后台维护的首页首屏介绍"
    assert updated_profile.json()["hero_skills"] == ["Vue", "FastAPI", "AI"]
    stats = client.get("/api/stats")
    assert stats.status_code == 200
    assert stats.json()["views_baseline"] == 1200
    assert stats.json()["total_views"] == stats.json()["actual_views"] + 1200
    assert stats.json()["published_posts"] > 0
    assert updated_profile.json()["stack"][-1] == {"group": "AI", "items": ["Codex", "Claude"]}
    assert client.get("/api/profile").json()["stack"][-1]["items"] == ["Codex", "Claude"]
    categories = client.get("/api/admin/categories", headers=headers)
    assert categories.status_code == 200
    assert categories.json()
    tags = client.get("/api/admin/tags", headers=headers)
    assert tags.status_code == 200
    assert tags.json()
    created = client.post("/api/admin/tags", headers=headers, json={"name": "临时测试标签"})
    assert created.status_code == 201
    public_tags = client.get("/api/tags").json()
    assert any(tag["name"] == "临时测试标签" and tag["count"] == 0 for tag in public_tags)
    assert client.delete(f"/api/admin/tags/{created.json()['slug']}", headers=headers).status_code == 204

    created_category = client.post("/api/admin/categories", headers=headers, json={"name": "临时测试分类"})
    assert created_category.status_code == 201
    public_categories = client.get("/api/categories").json()
    assert any(category["name"] == "临时测试分类" and category["count"] == 0 for category in public_categories)
    assert client.delete(
        f"/api/admin/categories/{created_category.json()['slug']}", headers=headers
    ).status_code == 204
