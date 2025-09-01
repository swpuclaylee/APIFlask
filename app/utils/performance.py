import time
import functools
from flask import request, current_app, g
import logging


# 性能监控装饰器
def monitor_performance(f):
    """API性能监控装饰器"""

    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()

        try:
            result = f(*args, **kwargs)
            end_time = time.time()

            # 记录性能指标
            duration = (end_time - start_time) * 1000  # 毫秒

            # 慢查询告警
            if duration > 1000:  # 超过1秒
                current_app.logger.warning(
                    f"Slow API: {request.method} {request.path} - {duration:.2f}ms"
                )

            # 记录到性能日志
            perf_logger = logging.getLogger('performance')
            perf_logger.info(
                f"API: {request.method} {request.path} | "
                f"Duration: {duration:.2f}ms | "
                f"User: {getattr(g, 'current_user_id', 'anonymous')}"
            )

            return result
        except Exception as e:
            end_time = time.time()
            duration = (end_time - start_time) * 1000
            current_app.logger.error(
                f"API Error: {request.method} {request.path} - {duration:.2f}ms - {str(e)}"
            )
            raise

    return decorated_function