from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.templates_config import templates
from app.database import get_db
from app.models.models import User
from app.auth import (
    hash_password, verify_password,
    create_session_token, SESSION_COOKIE, get_current_user
)

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("user/login.html", {"request": request, "user": None, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    db_user = db.query(User).filter(User.username == username, User.is_active == True).first()
    if not db_user or not verify_password(password, db_user.hashed_password):
        return templates.TemplateResponse(
            "user/login.html",
            {"request": request, "user": None, "error": "Invalid username or password"},
            status_code=401,
        )
    token = create_session_token(db_user.id)
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(SESSION_COOKIE, token, httponly=True, max_age=86400 * 7, samesite="lax")
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(SESSION_COOKIE)
    return response
