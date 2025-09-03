from typing import List

from app.models.user import User


class PermissionService:
    """权限管理服务类 - 负责权限验证和管理逻辑"""

    @staticmethod
    def get_user_permissions(user_id: int) -> List[str]:
        """
        获取用户的所有权限列表
        原理：通过用户->角色->权限的关联关系，获取用户拥有的所有权限
        """
        user = User.query.get(user_id)
        if not user or not user.is_active:
            return []

        permissions = set()
        for role in user.roles:
            if role.is_active:
                for permission in role.permissions:
                    if permission.is_active:
                        permissions.add(permission.name)

        return list(permissions)

    @staticmethod
    def check_permission(user_id: int, permission_name: str) -> bool:
        """
        检查用户是否拥有特定权限
        Args:
            user_id: 用户ID
            permission_name: 权限名称，格式：resource:action
        """
        user_permissions = PermissionService.get_user_permissions(user_id)
        return permission_name in user_permissions

    @staticmethod
    def check_resource_action(user_id: int, resource: str, action: str) -> bool:
        """
        检查用户对特定资源的操作权限
        Args:
            user_id: 用户ID
            resource: 资源名称
            action: 操作类型
        """
        permission_name = f"{resource}:{action}"
        return PermissionService.check_permission(user_id, permission_name)

    @staticmethod
    def has_role(user_id: int, role_name: str) -> bool:
        """检查用户是否拥有特定角色"""
        user = User.query.get(user_id)
        if not user:
            return False

        for role in user.roles:
            if role.name == role_name and role.is_active:
                return True
        return False
