from app import db
from .base import BaseModel


class Permission(BaseModel):
    """权限模型"""
    name = db.Column(db.String(100), unique=True, nullable=False)  # 如：user:read, order:create
    description = db.Column(db.String(255))
    resource = db.Column(db.String(50), nullable=False)  # 资源名称：user, order, product
    action = db.Column(db.String(50), nullable=False)  # 操作：create, read, update, delete
    is_active = db.Column(db.Boolean, default=True)
