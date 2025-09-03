from sqlalchemy.exc import IntegrityError

from app import db
from app.models.user import User


class UserService:
    """用户服务类"""

    @staticmethod
    def create_user(username, email, password, **kwargs):
        """创建用户"""
        try:
            user = User(
                username=username,
                email=email,
                **kwargs
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValueError('Username or email already exists')

    @staticmethod
    def get_user_by_id(user_id):
        """根据ID获取用户"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username):
        """根据用户名获取用户"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def get_user_by_email(email):
        """根据邮箱获取用户"""
        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_users(page=1, per_page=20, query=None, is_active=None, is_admin=None):
        """获取用户列表（分页）"""
        user_query  = User.query
        if query:
            search = f"%{query}%"
            user_query = user_query.filter(
                db.or_(
                    User.username.ilike(search),
                    User.email.ilike(search)
                )
            )

        if is_active is not None:
            user_query = user_query.filter(User.is_active == is_active)

        if is_admin is not None:
            user_query = user_query.filter(User.is_admin == is_admin)

        users = user_query.paginate(page=page, per_page=per_page, error_out=False)
        return users

    @staticmethod
    def update_user(user_id, **kwargs):
        """更新用户"""
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        for key, value in kwargs.items():
            setattr(user, key, value)
        try:
            db.session.commit()
            return user
        except IntegrityError:
            db.session.rollback()
            raise ValueError('Update failed: duplicate data')

    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        user = UserService.get_user_by_id(user_id)
        if not user:
            raise ValueError('User not found')
        try:
            db.session.delete(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            raise ValueError('Delete failed')
