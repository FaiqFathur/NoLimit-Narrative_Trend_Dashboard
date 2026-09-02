from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta

from app.api.dependencies import get_db
from models import Post, Topic
from app.core.cache import in_memory_cache

router = APIRouter()

@router.get("/overview")
@in_memory_cache(ttl_seconds=60)
def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Mengambil data agregasi total untuk ringkasan dashboard (KPI).
    """
    total_posts = db.query(func.count(Post.id)).scalar() or 0
    total_topics = db.query(func.count(Topic.id)).scalar() or 0
    
    # Agregasi total interaksi
    interactions = db.query(
        func.sum(Post.likes).label("total_likes"),
        func.sum(Post.comments).label("total_comments"),
        func.sum(Post.shares).label("total_shares"),
        func.sum(Post.views).label("total_views")
    ).first()
    
    total_likes = interactions.total_likes or 0
    total_comments = interactions.total_comments or 0
    total_shares = interactions.total_shares or 0
    total_views = interactions.total_views or 0
    
    return {
        "kpi": {
            "total_posts": total_posts,
            "total_topics": total_topics,
            "total_engagement": total_likes + total_comments + total_shares
        },
        "breakdown": {
            "likes": total_likes,
            "comments": total_comments,
            "shares": total_shares,
            "views": total_views
        }
    }

@router.get("/timeline")
@in_memory_cache(ttl_seconds=60)
def get_dashboard_timeline(days: int = 7, db: Session = Depends(get_db)):
    """
    Mengambil data jumlah post harian untuk dirender di Line Chart.
    """
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Group by Date
    daily_stats = db.query(
        cast(Post.created_at, Date).label("date"),
        func.count(Post.id).label("count")
    ).filter(Post.created_at >= start_date) \
     .group_by(cast(Post.created_at, Date)) \
     .order_by(cast(Post.created_at, Date)).all()
    
    timeline = [{"date": str(stat.date), "count": stat.count} for stat in daily_stats]
    
    return {
        "days_requested": days,
        "timeline": timeline
    }

@router.get("/sentiment")
@in_memory_cache(ttl_seconds=60)
def get_dashboard_sentiment(db: Session = Depends(get_db)):
    """
    Mengambil distribusi sentimen (positive, neutral, negative) untuk Pie/Donut Chart.
    """
    sentiment_counts = db.query(
        Post.sentiment,
        func.count(Post.id).label("count")
    ).group_by(Post.sentiment).all()
    
    distribution = {
        "positive": 0,
        "neutral": 0,
        "negative": 0,
        "unlabeled": 0
    }
    
    for stat in sentiment_counts:
        key = stat.sentiment.lower() if stat.sentiment else "unlabeled"
        if key in distribution:
            distribution[key] += stat.count
        else:
            distribution["unlabeled"] += stat.count
            
    return distribution

@router.get("/topics")
@in_memory_cache(ttl_seconds=60)
def get_dashboard_topics(limit: int = 10, db: Session = Depends(get_db)):
    """
    Mengambil daftar Trending Topics teratas beserta jumlah sebutannya (post count).
    """
    top_topics = db.query(Topic).order_by(Topic.post_count.desc()).limit(limit).all()
    
    topics_list = [
        {
            "id": t.id,
            "name": t.name,
            "post_count": t.post_count,
            "keywords": t.keywords
        }
        for t in top_topics
    ]
    
    return {
        "limit": limit,
        "trending_topics": topics_list
    }
