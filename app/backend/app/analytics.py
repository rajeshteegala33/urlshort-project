from sqlalchemy.orm import Session
from . import models

def record_click(db: Session, url_obj: models.URL, referrer: str = None, user_agent: str = None, ip: str = None):
    click = models.Click(url_id=url_obj.id, referrer=referrer, user_agent=user_agent, ip=ip)
    db.add(click)
    db.commit()
    db.refresh(click)
    return click

def get_analytics(db: Session, url_obj: models.URL, limit: int = 100):
    clicks = db.query(models.Click).filter(models.Click.url_id == url_obj.id).order_by(models.Click.timestamp.desc()).limit(limit).all()
    total = db.query(models.Click).filter(models.Click.url_id == url_obj.id).count()
    return total, clicks
