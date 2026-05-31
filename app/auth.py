import os
import bcrypt
from itsdangerous import URLSafeTimedSerializer
from fastapi import Request, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production-12345")
SESSION_COOKIE = "kb_session"

serializer = URLSafeTimedSerializer(SECRET_KEY)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_session_token(user_id: int) -> str:
    return serializer.dumps(user_id, salt="session")


def decode_session_token(token: str, max_age: int = 86400 * 7):
    try:
        return serializer.loads(token, salt="session", max_age=max_age)
    except Exception:
        return None


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    user_id = decode_session_token(token)
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id, User.is_active == True).first()


def require_admin(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user or user.role != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Admin access required")
    return user
