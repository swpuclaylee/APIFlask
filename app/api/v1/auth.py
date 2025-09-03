from flask_jwt_extended import jwt_required, get_jwt

from app.schemas import (
    LoginSchema,
    PasswordChangeSchema,
    ResponseSchema,
    UserRegisterSchema,
    UserSchema
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils import success_response, error_response
from . import auth_bp as bp


@bp.post('/auth/register')
@bp.input(UserRegisterSchema)
@bp.output(ResponseSchema)
@bp.doc(
    summary='用户注册',
    description='注册新用户并返回访问令牌'
)
def register(json_data):
    """用户注册"""
    try:
        # 创建用户
        user = UserService.create_user(
            username=json_data['username'],
            email=json_data['email'],
            password=json_data['password']
        )

        # 生成令牌
        tokens = AuthService.generate_tokens(user)
        return success_response(tokens)

    except Exception as e:
        return error_response(f'注册失败：{e}')


@bp.post('/auth/login')
@bp.input(LoginSchema)
@bp.output(ResponseSchema)
@bp.doc(
    summary='用户登录',
    description='用户登录并返回访问令牌和刷新令牌'
)
def login(json_data):
    """用户登录"""
    user, error = AuthService.authenticate_user(
        json_data['username'],
        json_data['password']
    )

    if error:
        return error_response(f'登录失败：{error}')

    tokens = AuthService.generate_tokens(user)
    return success_response(tokens)


@bp.post('/auth/refresh')
@bp.output(ResponseSchema)
@bp.doc(
    summary='刷新访问令牌',
    description='使用刷新令牌获取新的访问令牌',
    security=[{'BearerAuth': []}]
)
@jwt_required(refresh=True)  # 需要refresh token
def refresh():
    """刷新访问令牌"""
    tokens, error = AuthService.refresh_access_token()

    if error:
        return error_response(f'token刷新失败：{error}')

    return success_response(tokens)


@bp.post('/auth/logout')
@bp.doc(
    summary='用户登出',
    description='撤销当前访问令牌',
    security=[{'BearerAuth': []}]
)
@bp.output(ResponseSchema)
@jwt_required()
def logout():
    """用户登出"""
    jti = get_jwt()['jti']  # 获取JWT ID
    try:
        AuthService.logout_user(jti)
        return success_response()
    except Exception as e:
        return error_response(f'登出失败：{e}')


@bp.get('/auth/me')
@bp.output(ResponseSchema)
@bp.doc(
    summary='获取当前用户信息',
    description='获取当前登录用户的详细信息',
    security=[{'BearerAuth': []}]
)
@jwt_required()
def get_current_user():
    """获取当前用户信息"""
    user = AuthService.get_current_user()
    if not user:
        return error_response('User not found')

    return success_response(UserSchema().dump(user))


@bp.put('/auth/change-password')
@bp.input(PasswordChangeSchema)
@bp.doc(
    summary='修改密码',
    description='修改当前用户的密码',
    security=[{'BearerAuth': []}]
)
@bp.output(ResponseSchema)
@jwt_required()
def change_password(json_data):
    """修改密码"""
    user = AuthService.get_current_user()
    if not user:
        return error_response('User not found')

    # 验证当前密码
    if not user.check_password(json_data['current_password']):
        return error_response('Invalid current password')

    # 设置新密码
    user.set_password(json_data['new_password'])
    try:
        user.save()
        return success_response()
    except Exception as e:
        return error_response(f'Failed to change password: {e}')
