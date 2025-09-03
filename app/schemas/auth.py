from marshmallow import fields, validate
from .base import BaseSchema


class LoginSchema(BaseSchema):
    """登录请求Schema"""
    username = fields.Str(required=True, error_messages={'required': 'Username is required'})
    password = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={'required': 'Password is required'}
    )


class PasswordChangeSchema(BaseSchema):
    """修改密码Schema"""
    current_password = fields.Str(required=True, load_only=True)
    new_password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6, max=128),
            validate.Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)',
                error='Password must contain at least one letter and one number'
            )
        ],
        load_only=True
    )
