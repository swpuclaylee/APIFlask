from apiflask import APIFlask
from flask import request, current_app
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.utils import (
    jwt_error_response,
    error_response,
    setup_logging
)
from config import config
from app.middleware import register_all_middleware
import logging
from werkzeug.exceptions import HTTPException

# 扩展实例（在应用上下文之外创建）
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name='development'):
    """"应用工厂函数"""
    config_obj = config[config_name]

    # 创建APIFlask应用实例
    app = APIFlask(
        __name__,
        title=config_obj.APIFLASK_TITLE,
        version=config_obj.APIFLASK_VERSION
    )

    # 加载配置
    app.config.from_object(config_obj)

    # 初始化，将db实例绑定到当前app
    db.init_app(app)
    migrate.init_app(app, db)
    from app import models

    # 初始化JWT
    jwt.init_app(app)

    # JWT配置回调
    configure_jwt(app)

    # 配置CORS
    configure_cors(app, config_name)

    # 注册蓝图
    register_blueprints(app)

    # 注册错误处理器
    register_error_handlers(app)

    # 日志
    setup_logging(app)

    register_all_middleware(app)

    return app


def register_blueprints(app):
    """注册蓝图"""
    # 导入蓝图
    from app.api.v1.auth import auth_bp
    from app.api.v1.users import users_bp

    users_bp.security = [{'BearerAuth': []}]
    auth_bp.security = [{'BearerAuth': []}]

    app.register_blueprint(users_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1')


def register_error_handlers(app):
    """注册错误处理器"""

    # HTTP 状态码错误处理器
    @app.errorhandler(400)
    def bad_request(error):
        return error_response(
            msg='Bad request', data={'description': str(error)},
            status_code=400
        )

    @app.errorhandler(403)
    def forbidden(error):
        return error_response(
            msg='Forbidden', data={'description': 'Access denied'},
            status_code=403
        )

    @app.errorhandler(404)
    def not_found(error):
        return error_response(
            msg='Resource not found', data={'path': request.path},
            status_code=404
        )

    @app.errorhandler(422)
    def validation_error(error):
        return error_response(
            msg='Validation failed', data={'details': getattr(error, 'detail', str(error))},
            status_code=422
        )

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return error_response(
            msg='Rate limit exceeded', data={'description': 'Too many requests'},
            status_code=429
        )

    # 通用 HTTP 异常处理器
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """处理所有 HTTP 异常"""
        return error_response(
            f'HTTP {error.code} Error',
            data={
                'code': error.code,
                'name': error.name,
                'description': error.description
            },
            status_code=error.code
        )

    # 最重要的：通用异常处理器
    @app.errorhandler(Exception)
    def handle_exception(error):
        """处理所有未捕获的异常"""
        logger = logging.getLogger('app')

        # 记录详细的错误信息
        logger.error(
            f"Unhandled exception in {request.method} {request.path}: {str(error)}",
            exc_info=True  # 这会记录完整的堆栈跟踪
        )

        # 判断是否是开发环境
        if current_app.debug:
            # 开发环境返回详细错误信息
            return error_response(
                'Internal server error',
                data={
                    'error_type': type(error).__name__,
                    'error_message': str(error),
                    'path': request.path,
                    'method': request.method
                },
                status_code=500
            )
        else:
            # 生产环境返回通用错误信息
            return error_response(
                msg='Internal server error',
                status_code=500
            )


def configure_jwt(app):
    """配置JWT回调函数"""

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """检查token是否被撤销（黑名单机制）"""
        from app.services.token_service import TokenService

        token_service = TokenService()
        jti = jwt_payload['jti']  # JWT ID
        return token_service.is_token_revoked(jti)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """token被撤销时的响应"""
        return jwt_error_response(
            msg='Token has been revoked, please login again',
            status_code=401
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """token过期时的响应"""
        return jwt_error_response(
            msg='Token has expired',
            status_code=401
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """无效token时的响应"""
        return jwt_error_response(
            msg=f'Invalid token signature',
            status_code=401
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """缺少token时的响应"""
        return jwt_error_response(
            msg='Authorization token required',
            status_code=401
        )

    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        """向JWT添加额外的声明"""
        from app.services.user_service import UserService
        user = UserService.get_user_by_id(identity)
        return {
            'is_admin': user.is_admin if user else False,
            'username': user.username if user else None
        }


def configure_cors(app, config_name):
    """配置CORS策略"""

    if config_name == 'development':
        # 允许所有源，方便开发
        CORS(app, resources={
            r'/api/*': {
                'origins': '*',
                'methods': ['GET', 'POST', 'PUT', 'DELETE'],
                'allow_headers': ['Content-Type', 'Authorization']
            }
        })

    else:
        # 生产环境 - 严格配置
        CORS(app, resources={
            r"/api/*": {  # 只对API路径启用CORS
                "origins": [  # 允许的源
                    "http://localhost:3000",  # React开发服务器
                    "http://localhost:8080",  # Vue开发服务器
                    "https://yourdomain.com"  # 生产环境域名
                ],
                "methods": ["GET", "POST", "PUT", "DELETE"],  # 允许的HTTP方法
                "allow_headers": [  # 允许的请求头
                    "Content-Type",
                    "Authorization",
                    "X-Requested-With",
                    "X-API-Key"
                ],
                "expose_headers": [  # 暴露给前端的响应头
                    "X-Total-Count",
                    "X-Page-Number"
                ],
                "supports_credentials": True,  # 支持cookie/认证信息
                "max_age": 3600  # 预检请求缓存时间(秒)
            }
        })
