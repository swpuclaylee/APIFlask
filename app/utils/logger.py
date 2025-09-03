import functools
import logging
import logging.handlers
import os
import time
from datetime import datetime

from flask import request, g, has_request_context


class CustomFormatter(logging.Formatter):
    """自定义日志格式器"""

    def format(self, record):
        # 添加用户上下文
        if has_request_context() and hasattr(g, 'current_user_id'):
            record.user_id = g.current_user_id
        else:
            record.user_id = 'anonymous'

        # 添加请求上下文
        if request:
            record.method = request.method
            record.url = request.url
            record.remote_addr = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            record.user_agent = request.headers.get('User-Agent', '')
        else:
            record.method = record.url = record.remote_addr = record.user_agent = ''

        record.timestamp = datetime.now().isoformat()
        return super().format(record)


def setup_logging(app):
    """设置应用日志系统"""

    # 1. 创建日志目录
    log_dir = app.config.get('LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))

    # 2. 创建处理器
    handlers = []

    # 应用主日志处理器
    app_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'app.log'),
        maxBytes=10 * 1024 * 1024, backupCount=5
    )
    app_handler.setLevel(log_level)
    app_handler.setFormatter(CustomFormatter(
        '[%(timestamp)s] %(levelname)s - %(name)s - %(user_id)s - %(method)s %(url)s - %(message)s'
    ))
    handlers.append(app_handler)

    # 错误日志处理器
    error_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'error.log'),
        maxBytes=10 * 1024 * 1024, backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(CustomFormatter(
        '[%(timestamp)s] %(levelname)s - %(name)s - %(user_id)s - %(method)s %(url)s\n'
        'Remote: %(remote_addr)s - UserAgent: %(user_agent)s\n'
        'Message: %(message)s\n%(pathname)s:%(lineno)d\n'
    ))
    handlers.append(error_handler)

    # API访问日志处理器
    access_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'access.log'),
        maxBytes=10 * 1024 * 1024, backupCount=7
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(CustomFormatter(
        '[%(timestamp)s] %(remote_addr)s - %(user_id)s - "%(method)s %(url)s" - %(message)s'
    ))

    # 开发环境控制台输出
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        handlers.append(console_handler)

    # 3. 配置根记录器
    logging.basicConfig(level=log_level, handlers=handlers)

    # 4. 创建专用记录器
    loggers = {
        'app': logging.getLogger('app'),
        'business': logging.getLogger('business'),
        'security': logging.getLogger('security'),
        'access': logging.getLogger('access'),
        'performance': logging.getLogger('performance')
    }

    # 5. 配置访问日志独立处理
    loggers['access'].addHandler(access_handler)
    loggers['access'].propagate = False

    return loggers


# API调用装饰器
def log_api_call(f):
    """自动记录API调用信息"""

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        access_logger = logging.getLogger('access')
        app_logger = logging.getLogger('app')

        try:
            app_logger.info(f"API Request: {request.method} {request.path}")
            result = f(*args, **kwargs)

            duration = (time.time() - start_time) * 1000
            status_code = result[1] if isinstance(result, tuple) else 200
            access_logger.info(f"{status_code} - {duration:.2f}ms")

            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            app_logger.error(f"API Error: {str(e)} - {duration:.2f}ms")
            raise

    return decorated_function
