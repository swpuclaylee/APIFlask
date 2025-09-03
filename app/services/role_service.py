from typing import Optional, List

from app import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User


class RoleService:
    """角色管理服务"""

    @staticmethod
    def create_role(name: str, description: str = "") -> Optional[Role]:
        """创建新角色"""
        # 检查角色名是否已存在
        existing_role = Role.query.filter_by(name=name).first()
        if existing_role:
            return None

        role = Role(name=name, description=description)
        db.session.add(role)
        db.session.commit()
        return role

    @staticmethod
    def update_role(role_id: int, name: str = None, description: str = None) -> bool:
        """更新角色信息"""
        role = Role.query.get(role_id)
        if not role:
            return False

        if name and name != role.name:
            # 检查新名称是否已存在
            existing = Role.query.filter_by(name=name).first()
            if existing:
                return False
            role.name = name

        if description is not None:
            role.description = description

        db.session.commit()
        return True

    @staticmethod
    def delete_role(role_id: int) -> bool:
        """删除角色（软删除）"""
        role = Role.query.get(role_id)
        if not role:
            return False

        role.is_active = False
        db.session.commit()
        return True

    @staticmethod
    def get_role_by_id(role_id: int) -> Optional[Role]:
        """根据ID获取角色"""
        return Role.query.get(role_id)

    @staticmethod
    def get_role_by_name(name: str) -> Optional[Role]:
        """根据名称获取角色"""
        return Role.query.filter_by(name=name, is_active=True).first()

    @staticmethod
    def get_all_roles() -> List[Role]:
        """获取所有活跃角色"""
        return Role.query.filter_by(is_active=True).all()

    @staticmethod
    def assign_permission_to_role(role_id: int, permission_name: str) -> bool:
        """为角色分配权限"""
        role = Role.query.get(role_id)
        permission = Permission.query.filter_by(name=permission_name, is_active=True).first()

        if not role or not permission:
            return False

        if permission not in role.permissions:
            role.permissions.append(permission)
            db.session.commit()

        return True

    @staticmethod
    def remove_permission_from_role(role_id: int, permission_name: str) -> bool:
        """移除角色的权限"""
        role = Role.query.get(role_id)
        permission = Permission.query.filter_by(name=permission_name).first()

        if not role or not permission:
            return False

        if permission in role.permissions:
            role.permissions.remove(permission)
            db.session.commit()

        return True

    @staticmethod
    def assign_permissions_to_role(role_id: int, permission_names: List[str]) -> bool:
        """批量为角色分配权限"""
        role = Role.query.get(role_id)
        if not role:
            return False

        permissions = Permission.query.filter(
            Permission.name.in_(permission_names),
            Permission.is_active == True
        ).all()

        # 清除现有权限
        role.permissions.clear()

        # 分配新权限
        for permission in permissions:
            role.permissions.append(permission)

        db.session.commit()
        return True

    @staticmethod
    def get_role_permissions(role_id: int) -> List[str]:
        """获取角色的权限列表"""
        role = Role.query.get(role_id)
        if not role:
            return []

        return [perm.name for perm in role.permissions if perm.is_active]

    @staticmethod
    def assign_role_to_user(user_id: int, role_name: str) -> bool:
        """为用户分配角色"""
        user = User.query.get(user_id)
        role = Role.query.filter_by(name=role_name, is_active=True).first()

        if not user or not role:
            return False

        if role not in user.roles:
            user.roles.append(role)
            db.session.commit()

        return True

    @staticmethod
    def remove_role_from_user(user_id: int, role_name: str) -> bool:
        """移除用户的角色"""
        user = User.query.get(user_id)
        role = Role.query.filter_by(name=role_name).first()

        if not user or not role:
            return False

        if role in user.roles:
            user.roles.remove(role)
            db.session.commit()

        return True

    @staticmethod
    def get_user_roles(user_id: int) -> List[str]:
        """获取用户的角色列表"""
        user = User.query.get(user_id)
        if not user:
            return []

        return [role.name for role in user.roles if role.is_active]
