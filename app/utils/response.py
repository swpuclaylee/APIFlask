def success_response(data=None, msg="success", paginate=None):
    """
    成功响应格式

    Args:
        data: 响应数据
        msg: 成功消息
        paginate: 分页信息 (可选)
    """
    response = {
        "code": 1,
        "msg": msg,
        "data": data
    }

    # 如果有分页信息则添加
    if paginate:
        response["paginate"] = paginate

    return response, 200


def error_response(msg="failed", data=None, status_code=500):
    """
    错误响应格式

    Args:
        msg: 错误消息
        data: 错误详细信息 (可选)
        status_code: 状态码
    """
    response = {
        "code": 0,
        "msg": msg,
        "data": data
    }

    return response, status_code


def paginate_response(pagination, schema_class, msg="success"):
    """
    通用分页响应格式

    Args:
        pagination: 分页对象 (Flask-SQLAlchemy pagination)
        schema_class: 序列化 Schema 类
        msg: 消息
    """
    # 直接实例化并设置 many=True
    items = schema_class(many=True).dump(pagination.items)

    paginate = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "total_pages": pagination.pages,
        "has_prev": pagination.has_prev,
        "has_next": pagination.has_next
    }

    return success_response(items, msg, paginate)


def jwt_error_response(msg, status_code=401):
    """
    jwt认证错误响应格式
    :param msg:
    :param status_code:
    :return:
    """
    return {
        "code": 0,
        "msg": msg,
        "data": None
    }, status_code
