from apiflask import APIFlask
from flask import request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.utils.response import jwt_error_response, error_response
from app.utils.logger import setup_logging
from config import config

# 扩展实例（在应用上下文之外创建）
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name='development'):
    """"应用工厂函数"""
    # 创建APIFlask应用实例
    app = APIFlask(__name__)

    app = APIFlask(__name__)

    # 直接配置安全方案
    app.config['OPENAPI_VERSION'] = '3.0.2'

    # 配置认证方案
    app.config['API_TITLE'] = 'Your API'
    app.config['API_VERSION'] = 'v1'

    # 在这里直接添加安全方案
    app.config['SECURITY_SCHEMES'] = {
        'bearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT'
        }
    }

    # 加载配置
    app.config.from_object(config[config_name])

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
    app.loggers = setup_logging(app)

    return app


def register_blueprints(app):
    """注册蓝图"""
    # 导入蓝图
    from app.api.v1 import users_bp, auth_bp, roles_bp

    app.register_blueprint(users_bp, url_prefix='/api/v1')
    app.register_blueprint(auth_bp, url_prefix='/api/v1')
    app.register_blueprint(roles_bp, url_prefix='/api/v1')


def register_error_handlers(app):
    """注册错误处理器"""

    @app.errorhandler(404)
    def not_found(error):
        return error_response('Resource not found', data={'path': request.path})

    @app.errorhandler(400)
    def bad_request(error):
        return error_response('Bad request', data={'description': str(error)})

    @app.errorhandler(500)
    def internal_error(error):
        # 生产环境不暴露具体错误信息
        return error_response('Internal server error')

    @app.errorhandler(422)
    def validation_error(error):
        return error_response(
            'Validation failed',
            data={'details': error.detail}
        )


def configure_jwt(app):
    """配置JWT回调函数"""

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        """检查token是否被撤销（黑名单机制）"""
        from app.services.token_service import TokenService

        jti = jwt_payload['jti']  # JWT ID
        return TokenService.is_token_revoked(jti)

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        """token被撤销时的响应"""
        return jwt_error_response('Token has been revoked, please login again')

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """token过期时的响应"""
        return jwt_error_response('Token has expired'), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        """无效token时的响应"""
        return jwt_error_response(f'Invalid token signature: {error}'), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        """缺少token时的响应"""
        return jwt_error_response(
            msg='Authorization token required',
            code=401
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
