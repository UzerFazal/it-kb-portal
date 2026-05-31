from fastapi import APIRouter, Request, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.templates_config import templates
from app.database import get_db
from app.models.models import Article, Category, Tag, User, article_tags
from app.auth import require_admin, get_current_user
import re
from datetime import datetime

router = APIRouter(prefix="/admin")


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


def unique_slug(base: str, db: Session, model, exclude_id: int = None) -> str:
    slug = slugify(base)
    candidate = slug
    n = 1
    while True:
        q = db.query(model).filter(model.slug == candidate)
        if exclude_id:
            q = q.filter(model.id != exclude_id)
        if not q.first():
            return candidate
        candidate = f"{slug}-{n}"
        n += 1


# ---------- Dashboard ----------

@router.get("/", response_class=HTMLResponse)
def admin_dashboard(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    total_articles = db.query(Article).count()
    published = db.query(Article).filter(Article.is_published == True).count()
    total_categories = db.query(Category).count()
    total_users = db.query(User).count()
    recent = db.query(Article).order_by(Article.updated_at.desc()).limit(10).all()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request, "user": admin,
        "total_articles": total_articles,
        "published": published,
        "total_categories": total_categories,
        "total_users": total_users,
        "recent": recent,
    })


# ---------- Articles ----------

@router.get("/articles", response_class=HTMLResponse)
def admin_articles(
    request: Request,
    page: int = Query(default=1),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)
    per_page = 20
    total = db.query(Article).count()
    articles = (
        db.query(Article)
        .order_by(Article.updated_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )
    return templates.TemplateResponse("admin/articles.html", {
        "request": request, "user": admin,
        "articles": articles, "page": page,
        "total_pages": (total + per_page - 1) // per_page,
    })


@router.get("/articles/new", response_class=HTMLResponse)
def article_new(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    categories = db.query(Category).order_by(Category.name).all()
    return templates.TemplateResponse("admin/article_form.html", {
        "request": request, "user": admin,
        "article": None, "categories": categories, "error": None,
    })


@router.post("/articles/new", response_class=HTMLResponse)
async def article_new_post(
    request: Request,
    title: str = Form(...),
    summary: str = Form(default=""),
    content: str = Form(...),
    category_id: int = Form(default=0),
    tags_raw: str = Form(default=""),
    is_published: str = Form(default="off"),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)
    slug = unique_slug(title, db, Article)
    article = Article(
        title=title.strip(),
        slug=slug,
        summary=summary.strip(),
        content=content,
        category_id=category_id if category_id else None,
        author_id=admin.id,
        is_published=(is_published == "on"),
    )
    # Tags
    for tag_name in [t.strip() for t in tags_raw.split(",") if t.strip()]:
        tag_slug = slugify(tag_name)
        tag = db.query(Tag).filter(Tag.slug == tag_slug).first()
        if not tag:
            tag = Tag(name=tag_name, slug=tag_slug)
            db.add(tag)
        article.tags.append(tag)
    db.add(article)
    db.commit()
    return RedirectResponse("/admin/articles", status_code=302)


@router.get("/articles/{article_id}/edit", response_class=HTMLResponse)
def article_edit(article_id: int, request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    article = db.query(Article).filter(Article.id == article_id).first()
    categories = db.query(Category).order_by(Category.name).all()
    tags_str = ", ".join(t.name for t in article.tags) if article else ""
    return templates.TemplateResponse("admin/article_form.html", {
        "request": request, "user": admin,
        "article": article, "categories": categories,
        "tags_str": tags_str, "error": None,
    })


@router.post("/articles/{article_id}/edit", response_class=HTMLResponse)
async def article_edit_post(
    article_id: int,
    request: Request,
    title: str = Form(...),
    summary: str = Form(default=""),
    content: str = Form(...),
    category_id: int = Form(default=0),
    tags_raw: str = Form(default=""),
    is_published: str = Form(default="off"),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return RedirectResponse("/admin/articles", status_code=302)
    article.title = title.strip()
    article.slug = unique_slug(title, db, Article, exclude_id=article_id)
    article.summary = summary.strip()
    article.content = content
    article.category_id = category_id if category_id else None
    article.is_published = (is_published == "on")
    article.updated_at = datetime.utcnow()
    # Rebuild tags
    article.tags.clear()
    for tag_name in [t.strip() for t in tags_raw.split(",") if t.strip()]:
        tag_slug = slugify(tag_name)
        tag = db.query(Tag).filter(Tag.slug == tag_slug).first()
        if not tag:
            tag = Tag(name=tag_name, slug=tag_slug)
            db.add(tag)
        article.tags.append(tag)
    db.commit()
    return RedirectResponse("/admin/articles", status_code=302)


@router.post("/articles/{article_id}/delete")
def article_delete(article_id: int, request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
    return RedirectResponse("/admin/articles", status_code=302)


# ---------- Categories ----------

@router.get("/categories", response_class=HTMLResponse)
def admin_categories(request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("admin/categories.html", {
        "request": request, "user": admin, "categories": categories,
    })


@router.post("/categories/new")
async def category_new(
    request: Request,
    name: str = Form(...),
    description: str = Form(default=""),
    icon: str = Form(default="folder"),
    order: int = Form(default=0),
    db: Session = Depends(get_db),
):
    admin = require_admin(request, db)
    slug = unique_slug(name, db, Category)
    cat = Category(name=name.strip(), slug=slug, description=description.strip(), icon=icon.strip(), order=order)
    db.add(cat)
    db.commit()
    return RedirectResponse("/admin/categories", status_code=302)


@router.post("/categories/{cat_id}/delete")
def category_delete(cat_id: int, request: Request, db: Session = Depends(get_db)):
    admin = require_admin(request, db)
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if cat:
        db.delete(cat)
        db.commit()
    return RedirectResponse("/admin/categories", status_code=302)
