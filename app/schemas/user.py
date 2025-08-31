from marshmallow import fields, validate

from .base import BaseSchema


class UserCreateSchema(BaseSchema):
    """用户创建schema"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    email = fields.Email(required=True, allow_none=False)
    password = fields.Str(required=True, load_only=True)


class UserUpdateSchema(BaseSchema):
    """用户更新schema"""
    username = fields.Str(validate=validate.Length(min=3, max=20))
    email = fields.Email()


class UserSchema(BaseSchema):
    """用户响应schema"""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    is_active = fields.Bool(dump_only=True)
    is_admin = fields.Bool(dump_only=True)


class UserQuerySchema(BaseSchema):
    """用户查询schema"""
    page = fields.Int(missing=1, validate=validate.Range(min=1))
    per_page = fields.Int(missing=10, validate=validate.Range(min=1, max=100))
    search = fields.Str(missing='')
    is_active = fields.Bool()


class UserRegisterSchema(BaseSchema):
    """用户注册schema"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    email = fields.Email(required=True, allow_none=False)
    password = fields.Str(required=True, load_only=True)
