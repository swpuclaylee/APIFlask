from apiflask import APIBlueprint
from flask_jwt_extended import jwt_required

from app.schemas import (
    ResponseSchema,
    UserCreateSchema,
    UserSchema,
    UserUpdateSchema,
    UserQuerySchema
)
from app.services import (
    UserService
)
from app.utils import (
    success_response,
    error_response,
    paginate_response,
    business_logger,
    api_endpoint
)

users_bp = APIBlueprint('users', __name__, url_prefix='/api/v1/users', tag='用户管理')


@users_bp.get('/users')
@users_bp.doc(security=[{'Bearer': []}])
@api_endpoint(
    bp=users_bp,
    schema_input=UserQuerySchema,
    schema_output=ResponseSchema,
    auth_required=True,
    log_calls=True
)
def get_users(query_data):
    """获取用户列表"""
    pagination = UserService.get_users(
        page=query_data.get('page', 1),
        per_page=query_data.get('per_page', 20),
        query=query_data.get('query'),
        is_active=query_data.get('is_active'),
        is_admin=query_data.get('is_admin')
    )
    return paginate_response(pagination, UserSchema)


@users_bp.get('/users/<int:user_id>')
@users_bp.output(ResponseSchema)
@jwt_required()
def get_user(user_id):
    """获取单个用户"""
    user = UserService.get_user_by_id(user_id)
    if not user:
        return error_response("用户不存在")
    return success_response(UserSchema().dump(user))


@users_bp.post('/users')
@users_bp.input(UserCreateSchema)
@users_bp.output(ResponseSchema)
@jwt_required()
def create_user(json_data):
    """创建用户"""
    try:
        user = UserService.create_user(**json_data)
        return success_response(UserSchema().dump(user))
    except Exception as e:
        return error_response(f'用户创建失败：{str(e)}')


@users_bp.put('/users/<int:user_id>')
@users_bp.input(UserUpdateSchema)
@users_bp.output(ResponseSchema)
@jwt_required()
def update_user(user_id, json_data):
    """更新用户"""
    try:
        user = UserService.update_user(user_id, **json_data)
        return success_response(UserSchema().dump(user))
    except Exception as e:
        return error_response(f'用户更新失败：{str(e)}')


@users_bp.delete('/users/<int:user_id>')
@users_bp.output(ResponseSchema)
@jwt_required()
def delete_user(user_id):
    """删除用户"""
    try:
        UserService.delete_user(user_id)
        return success_response()
    except Exception as e:
        return error_response(f'用户删除失败：{str(e)}')
