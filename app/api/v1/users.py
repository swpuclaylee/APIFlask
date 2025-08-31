from flask_jwt_extended import jwt_required

from app.schemas import (
    ResponseSchema,
    UserCreateSchema,
    UserSchema,
    UserUpdateSchema,
    UserQuerySchema
)
from app.services.user_service import UserService
from app.utils import (
    success_response,
    error_response,
    paginate_response
)
from . import users_bp as bp


@bp.get('/users')
@bp.input(UserQuerySchema, location='query')
@bp.output(ResponseSchema)
@jwt_required()
def get_users(query_params):
    """获取用户列表"""

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
@jwt_required()
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
