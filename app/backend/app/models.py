"""
SQLAlchemy models: User, URL, Click
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Text
from sqlalchemy.orm import relationship
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    urls = relationship("URL", back_populates="owner")

class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    short = Column(String(32), unique=True, index=True, nullable=False)
    original = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    clicks = relationship("Click", back_populates="url")
    owner = relationship("User", back_populates="urls")

class Click(Base):
    __tablename__ = "clicks"
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    referrer = Column(String(512), nullable=True)
    user_agent = Column(String(512), nullable=True)
    ip = Column(String(64), nullable=True)
    url = relationship("URL", back_populates="clicks")
