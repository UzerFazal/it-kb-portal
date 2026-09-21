from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean,
    ForeignKey, Table
)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

# Many-to-many: articles <-> tags
article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(128), unique=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    role = Column(String(16), default="user")  # "user" or "admin"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), unique=True, nullable=False)
    slug = Column(String(128), unique=True, nullable=False)
    icon = Column(String(64), default="folder")   # Lucide icon name
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    name_cs = Column(String(128), nullable=True)
    description_cs = Column(Text, nullable=True)

    articles = relationship("Article", back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, nullable=False)
    slug = Column(String(64), unique=True, nullable=False)

    articles = relationship("Article", secondary=article_tags, back_populates="tags")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), nullable=False)
    slug = Column(String(256), unique=True, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)   # HTML / markdown stored as HTML
    title_cs = Column(String(256), nullable=True)
    summary_cs = Column(Text, nullable=True)
    content_cs = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_published = Column(Boolean, default=True)
    views = Column(Integer, default=0)
    helpful_yes = Column(Integer, default=0)
    helpful_no = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("Category", back_populates="articles")
    author = relationship("User")
    tags = relationship("Tag", secondary=article_tags, back_populates="articles")
