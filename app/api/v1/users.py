from flask import current_app
from flask_jwt_extended import jwt_required

from app.schemas.base import ResponseSchema
from app.schemas.user import UserCreateSchema, UserSchema, UserUpdateSchema, UserQuerySchema
from app.services.user_service import UserService
from app.utils.logger import log_api_call
from app.utils.permissions import Permissions
from app.utils.permissions import require_permission, require_resource_action
from app.utils.response import success_response, error_response, paginate_response
from . import users_bp as bp


@log_api_call
@bp.get('/users')
@bp.input(UserQuerySchema, location='query')
@bp.output(ResponseSchema)
@require_permission(Permissions.USER_READ)
def get_users(query_params):
    """获取用户列表"""
    current_app.loggers['business'].info('获取用户列表')
    pagination = UserService.get_users(
        page=query_params.get('page', 1),
        per_page=query_params.get('per_page', 20),
        query=query_params.get('query'),
        is_active=query_params.get('is_active'),
        is_admin=query_params.get('is_admin')
    )

    return paginate_response(pagination, UserSchema)


@bp.get('/users/<int:user_id>')
@bp.output(ResponseSchema)
@jwt_required()
def get_user(user_id):
    """获取单个用户"""
    user = UserService.get_user_by_id(user_id)
    if not user:
        return error_response("用户不存在")
    return success_response(UserSchema().dump(user))


@bp.post('/users')
@bp.input(UserCreateSchema)
@bp.output(ResponseSchema)
@require_resource_action('user', 'create')
def create_user(json_data):
    """创建用户"""
    try:
        user = UserService.create_user(**json_data)
        return success_response(UserSchema().dump(user))
    except Exception as e:
        return error_response(f'用户创建失败：{str(e)}')


@bp.put('/users/<int:user_id>')
@bp.input(UserUpdateSchema)
@bp.output(ResponseSchema)
@jwt_required()
def update_user(user_id, json_data):
    """更新用户"""
    try:
        user = UserService.update_user(user_id, **json_data)
        return success_response(UserSchema().dump(user))
    except Exception as e:
        return error_response(f'用户更新失败：{str(e)}')


@bp.delete('/users/<int:user_id>')
@bp.output(ResponseSchema)
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    try:
        UserService.delete_user(user_id)
        return success_response()
    except Exception as e:
        return error_response(f'用户删除失败：{str(e)}')


# @app.post('/users/<int:user_id>/roles')
# @require_permission(Permissions.ROLE_UPDATE)
# def assign_role_to_user_api(user_id):
#     """为用户分配角色 - 需要角色更新权限"""
#     # 示例数据，实际应从request.json获取
#     data = {
#         "role_name": Roles.USER
#     }
#
#     success = RoleService.assign_role_to_user(user_id, data["role_name"])
#     if success:
#         return {"message": f"角色 {data['role_name']} 分配成功"}
#     else:
#         abort(400, message="角色分配失败")
#
#
# @app.delete('/users/<int:user_id>/roles/<string:role_name>')
# @require_permission(Permissions.ROLE_UPDATE)
# def remove_role_from_user_api(user_id, role_name):
#     """移除用户角色 - 需要角色更新权限"""
#     success = RoleService.remove_role_from_user(user_id, role_name)
#     if success:
#         return {"message": f"角色 {role_name} 移除成功"}
#     else:
#         abort(400, message="角色移除失败")
#
#
# @app.get('/users/<int:user_id>/roles')
# @require_permission(Permissions.USER_READ)
# def get_user_roles_api(user_id):
#     """获取用户的角色列表 - 需要用户查看权限"""
#     roles = RoleService.get_user_roles(user_id)
#     return {"roles": roles}
