from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.templates_config import templates
from app.database import get_db
from app.models.models import Article, Category, Tag
from app.auth import get_current_user

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    categories = db.query(Category).order_by(Category.order).all()
    # Count published articles per category
    for cat in categories:
        cat.article_count = db.query(Article).filter(
            Article.category_id == cat.id,
            Article.is_published == True
        ).count()
    popular = (
        db.query(Article)
        .filter(Article.is_published == True)
        .order_by(Article.views.desc())
        .limit(5)
        .all()
    )
    recent = (
        db.query(Article)
        .filter(Article.is_published == True)
        .order_by(Article.updated_at.desc())
        .limit(5)
        .all()
    )
    total_articles = db.query(Article).filter(Article.is_published == True).count()
    return templates.TemplateResponse("user/home.html", {
        "request": request,
        "user": user,
        "categories": categories,
        "popular": popular,
        "recent": recent,
        "total_articles": total_articles,
    })


@router.get("/search", response_class=HTMLResponse)
def search(
    request: Request,
    q: str = Query(default="", alias="q"),
    category: str = Query(default=""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    results = []
    categories = db.query(Category).order_by(Category.order).all()

    if q.strip():
        query = db.query(Article).filter(Article.is_published == True)
        # Full-text keyword search across title, summary, content
        search_term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Article.title.ilike(search_term),
                Article.summary.ilike(search_term),
                Article.content.ilike(search_term),
            )
        )
        if category:
            cat_obj = db.query(Category).filter(Category.slug == category).first()
            if cat_obj:
                query = query.filter(Article.category_id == cat_obj.id)
        results = query.order_by(Article.views.desc()).limit(50).all()

    return templates.TemplateResponse("user/search.html", {
        "request": request,
        "user": user,
        "q": q,
        "results": results,
        "categories": categories,
        "selected_category": category,
    })


@router.get("/category/{slug}", response_class=HTMLResponse)
def category_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    cat = db.query(Category).filter(Category.slug == slug).first()
    if not cat:
        return templates.TemplateResponse("user/404.html", {"request": request, "user": user}, status_code=404)
    articles = (
        db.query(Article)
        .filter(Article.category_id == cat.id, Article.is_published == True)
        .order_by(Article.title)
        .all()
    )
    all_categories = db.query(Category).order_by(Category.order).all()
    return templates.TemplateResponse("user/category.html", {
        "request": request,
        "user": user,
        "category": cat,
        "articles": articles,
        "all_categories": all_categories,
    })


@router.get("/article/{slug}", response_class=HTMLResponse)
def article_detail(slug: str, request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    article = db.query(Article).filter(
        Article.slug == slug,
        Article.is_published == True,
    ).first()
    if not article:
        return templates.TemplateResponse("user/404.html", {"request": request, "user": user}, status_code=404)
    # Increment view count
    article.views += 1
    db.commit()
    # Related articles (same category, excluding self)
    related = (
        db.query(Article)
        .filter(
            Article.category_id == article.category_id,
            Article.id != article.id,
            Article.is_published == True,
        )
        .limit(4)
        .all()
    )
    return templates.TemplateResponse("user/article.html", {
        "request": request,
        "user": user,
        "article": article,
        "related": related,
    })


@router.post("/article/{slug}/helpful", response_class=HTMLResponse)
async def article_helpful(slug: str, request: Request, db: Session = Depends(get_db)):
    from fastapi.responses import JSONResponse
    article = db.query(Article).filter(Article.slug == slug).first()
    if not article:
        return JSONResponse({"error": "not found"}, status_code=404)
    form = await request.form()
    vote = form.get("vote")
    if vote == "yes":
        article.helpful_yes += 1
    elif vote == "no":
        article.helpful_no += 1
    db.commit()
    return JSONResponse({"yes": article.helpful_yes, "no": article.helpful_no})
