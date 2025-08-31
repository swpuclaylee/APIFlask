from datetime import datetime
from app import db


class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow().replace(microsecond=0), nullable=False,
                           onupdate=datetime.utcnow().replace(microsecond=0))
