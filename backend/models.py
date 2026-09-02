import uuid
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, MetaData, Float, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import declarative_base
from datetime import datetime

metadata = MetaData()
Base = declarative_base(metadata=metadata)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    keywords = Column(ARRAY(Text), nullable=True)
    post_count = Column(Integer, default=0)
    first_seen = Column(DateTime, nullable=True)
    last_seen = Column(DateTime, nullable=True)

class Entity(Base):
    __tablename__ = 'entities'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False) # e.g., 'person', 'organization', 'location', 'event'
    mention_count = Column(Integer, default=0)

class Post(Base):
    __tablename__ = 'posts'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(50), nullable=False, index=True) # 'twitter', 'tiktok', 'instagram'
    platform_post_id = Column(String(100), nullable=False, unique=True)
    author_username = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    hashtags = Column(ARRAY(Text), nullable=True)
    posted_at = Column(DateTime, nullable=True, index=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    sentiment = Column(String(20), nullable=True, index=True) # 'positive', 'negative', 'neutral'
    sentiment_score = Column(Float, nullable=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
