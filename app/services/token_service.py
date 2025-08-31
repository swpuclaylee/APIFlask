from datetime import timedelta

import redis
from flask import current_app


class TokenService:
    def __init__(self):
        self.redis_client = redis.from_url(current_app.config.get('REDIS_URL', 'redis://localhost:6379/0'))

    def revoke_token(self, jti, expires_in=None):
        """撤销token（加入黑名单）"""
        if expires_in is None:
            expires_in = timedelta(hours=1).total_seconds()  # 默认1小时过期

        self.redis_client.setex(
            f"blacklist:{jti}",
            int(expires_in),
            "revoked"
        )

    def is_token_revoked(self, jti):
        """检查token是否已被撤销"""
        return self.redis_client.exists(f"blacklist:{jti}")

    def revoke_all_user_tokens(self, user_id):
        """撤销用户的所有token"""
        # 在实际应用中，可以维护用户token列表
        # 这里简化处理
        pass
