from .auth import register_auth_middleware


def register_all_middleware(app):
    register_auth_middleware(app)
