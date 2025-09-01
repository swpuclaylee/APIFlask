from app import db
from .base import BaseModel

# 角色权限关联表（多对多）
role_permissions = db.Table('role_permissions',
                            db.Column('role_id', db.Integer, db.ForeignKey('role.id'), primary_key=True),
                            db.Column('permission_id', db.Integer, db.ForeignKey('permission.id'), primary_key=True)
                            )


class Role(BaseModel):
    """角色模型"""
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)

    # 多对多关系：角色-权限
    permissions = db.relationship('Permission', secondary=role_permissions,
                                  backref=db.backref('roles', lazy='dynamic'))
