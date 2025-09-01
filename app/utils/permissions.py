from functools import wraps
from typing import List

from apiflask import abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.permission_service import PermissionService


# 预定义权限常量
class Permissions:
    """权限常量类 - 统一管理所有权限名称"""

    # 用户管理权限
    USER_CREATE = 'user:create'
    USER_READ = 'user:read'
    USER_UPDATE = 'user:update'
    USER_DELETE = 'user:delete'

    # 角色管理权限
    ROLE_CREATE = 'role:create'
    ROLE_READ = 'role:read'
    ROLE_UPDATE = 'role:update'
    ROLE_DELETE = 'role:delete'

    # 权限管理权限
    PERMISSION_CREATE = 'permission:create'
    PERMISSION_READ = 'permission:read'
    PERMISSION_UPDATE = 'permission:update'
    PERMISSION_DELETE = 'permission:delete'

    # 订单管理权限
    ORDER_CREATE = 'order:create'
    ORDER_READ = 'order:read'
    ORDER_UPDATE = 'order:update'
    ORDER_DELETE = 'order:delete'

    # 产品管理权限
    PRODUCT_CREATE = 'product:create'
    PRODUCT_READ = 'product:read'
    PRODUCT_UPDATE = 'product:update'
    PRODUCT_DELETE = 'product:delete'

    # 报告权限
    REPORT_READ = 'report:read'
    REPORT_MANAGE = 'report:manage'

    # 系统权限
    SYSTEM_CONFIG = 'system:config'
    SYSTEM_LOG = 'system:log'

    @classmethod
    def get_all_permissions(cls):
        """获取所有权限列表"""
        return [getattr(cls, attr) for attr in dir(cls)
                if not attr.startswith('_') and attr != 'get_all_permissions']


class Roles:
    """角色常量类 - 统一管理所有角色名称"""

    SUPER_ADMIN = 'super_admin'
    ADMIN = 'admin'
    USER_MANAGER = 'user_manager'
    ORDER_MANAGER = 'order_manager'
    PRODUCT_MANAGER = 'product_manager'
    CUSTOMER_SERVICE = 'customer_service'
    FINANCE = 'finance'
    USER = 'user'
    GUEST = 'guest'


def require_permission(permission_name: str):
    """
    权限验证装饰器 - 验证用户是否拥有指定权限

    原理：
    1. 结合@jwt_required()使用，确保用户已登录
    2. 从JWT token中获取用户ID
    3. 通过PermissionService检查权限
    4. 权限不足时返回403错误

    使用方式：@require_permission('user:read')
    """

    def decorator(f):
        @wraps(f)
        @jwt_required()  # 确保用户已登录
        def decorated_function(*args, **kwargs):
            # 获取当前用户ID
            current_user_id = get_jwt_identity()

            # 检查权限
            if not PermissionService.check_permission(current_user_id, permission_name):
                abort(403, message=f"权限不足，需要权限: {permission_name}")

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_resource_action(resource: str, action: str):
    """
    资源操作权限装饰器

    使用方式：@require_resource_action('user', 'read')
    等同于：@require_permission('user:read')
    """

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()

            if not PermissionService.check_resource_action(current_user_id, resource, action):
                abort(403, message=f"权限不足，需要对资源 {resource} 进行 {action} 操作的权限")

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_role(role_name: str):
    """
    角色验证装饰器

    使用方式：@require_role('admin')
    """

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()

            if not PermissionService.has_role(current_user_id, role_name):
                abort(403, message=f"权限不足，需要角色: {role_name}")

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_any_permission(permission_list: List[str]):
    """
    多权限验证装饰器 - 用户拥有任一权限即可

    使用方式：@require_any_permission(['user:read', 'user:update'])
    """

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()

            # 检查是否拥有任一权限
            has_permission = any(
                PermissionService.check_permission(current_user_id, perm)
                for perm in permission_list
            )

            if not has_permission:
                abort(403, message=f"权限不足，需要以下任一权限: {', '.join(permission_list)}")

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def require_all_permissions(permission_list: List[str]):
    """
    多权限验证装饰器 - 用户必须拥有所有权限

    使用方式：@require_all_permissions(['user:read', 'user:update'])
    """

    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()

            # 检查是否拥有所有权限
            for perm in permission_list:
                if not PermissionService.check_permission(current_user_id, perm):
                    abort(403, message=f"权限不足，缺少权限: {perm}")

            return f(*args, **kwargs)

        return decorated_function

    return decorator
