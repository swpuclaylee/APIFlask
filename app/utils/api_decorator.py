from flask_jwt_extended import jwt_required

from .logger import log_api_call


def api_endpoint(bp, schema_input=None, schema_output=None, auth_required=True, log_calls=True):
    """通用API端点装饰器"""

    def decorator(f):
        # 应用多个装饰器
        if schema_output:
            f = bp.output(schema_output)(f)
        if schema_input:
            f = bp.input(schema_input, location='query')(f)
        if auth_required:
            f = jwt_required()(f)
        if log_calls:
            f = log_api_call(f)
        return f

    return decorator
