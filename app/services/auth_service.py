from datetime import timedelta

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity

from app.services import UserService, TokenService


class AuthService:
    @staticmethod
    def authenticate_user(username, password):
        """用户认证"""
        user = UserService.get_user_by_username(username)

        if not user or not user.check_password(password):
            return None, "Invalid username or password"

        if not user.is_active:
            return None, "Account has been deactivated"

        return user, None

    @staticmethod
    def generate_tokens(user):
        """生成访问令牌和刷新令牌"""
        # 额外的身份信息
        additional_claims = {
            'username': user.username,
            'is_admin': user.is_admin,
            'email': user.email
        }

        # 生成访问令牌（短期）
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=1)
        )

        # 生成刷新令牌（长期）
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600,  # 1小时，以秒为单位
        }

    @staticmethod
    def refresh_access_token():
        """刷新访问令牌"""
        current_user_id = get_jwt_identity()
        user = UserService.get_user_by_id(current_user_id)

        if not user or not user.is_active:
            return None, "User not found or inactive"

        # 生成新的访问令牌
        additional_claims = {
            'username': user.username,
            'is_admin': user.is_admin,
            'email': user.email
        }

        new_access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=1)
        )

        return {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': 3600
        }, None

    @staticmethod
    def logout_user(jti):
        """用户登出（将token加入黑名单）"""
        TokenService.revoke_token(jti)
        return True

    @staticmethod
    def get_current_user():
        """获取当前登录用户"""
        current_user_id = get_jwt_identity()
        if current_user_id:
            return UserService.get_user_by_id(current_user_id)
        return None
