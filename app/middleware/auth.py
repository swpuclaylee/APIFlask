from flask import g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request


def load_user_context():
    """加载用户上下文中间件"""
    try:
        verify_jwt_in_request(optional=True)
        g.current_user_id = get_jwt_identity() or 'anonymous'
    except:
        g.current_user_id = 'anonymous'


def register_auth_middleware(app):
    """注册认证中间件"""
    app.before_request(load_user_context)
