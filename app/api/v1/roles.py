from flask_jwt_extended import jwt_required, get_jwt

from app.schemas import (
    LoginSchema,
    PasswordChangeSchema,
    UserRegisterSchema,
    UserSchema,
    ResponseSchema
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils import (
    success_response,
    error_response
)
from . import roles_bp as bp


@app.post('/roles')
@require_permission(Permissions.ROLE_CREATE)
def create_role_api():
    """创建角色 - 需要角色创建权限"""
    # 这里应该使用APIFlask的Schema验证请求体
    # 示例数据，实际应从request.json获取
    data = {
        "name": "custom_role",
        "description": "自定义角色"
    }

    role = RoleService.create_role(data["name"], data.get("description", ""))
    if role:
        return {"message": "角色创建成功", "role": {"id": role.id, "name": role.name}}
    else:
        abort(400, message="角色创建失败，可能角色名已存在")


@app.get('/roles')
@require_permission(Permissions.ROLE_READ)
def get_roles_api():
    """获取角色列表 - 需要角色查看权限"""
    roles = RoleService.get_all_roles()
    return {
        "roles": [
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "is_active": role.is_active
            } for role in roles
        ]
    }


@app.get('/roles/<int:role_id>')
@require_permission(Permissions.ROLE_READ)
def get_role_api(role_id):
    """获取角色详情 - 需要角色查看权限"""
    role = RoleService.get_role_by_id(role_id)
    if not role:
        abort(404, message="角色不存在")

    permissions = RoleService.get_role_permissions(role_id)
    return {
        "role": {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "is_active": role.is_active,
            "permissions": permissions
        }
    }


@app.put('/roles/<int:role_id>')
@require_permission(Permissions.ROLE_UPDATE)
def update_role_api(role_id):
    """更新角色信息 - 需要角色更新权限"""
    # 示例数据，实际应从request.json获取
    data = {
        "name": "updated_role",
        "description": "更新后的角色描述"
    }

    success = RoleService.update_role(role_id, data.get("name"), data.get("description"))
    if success:
        return {"message": "角色更新成功"}
    else:
        abort(400, message="角色更新失败")


@app.delete('/roles/<int:role_id>')
@require_permission(Permissions.ROLE_DELETE)
def delete_role_api(role_id):
    """删除角色 - 需要角色删除权限"""
    success = RoleService.delete_role(role_id)
    if success:
        return {"message": "角色删除成功"}
    else:
        abort(404, message="角色不存在")
