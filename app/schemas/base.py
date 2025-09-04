from marshmallow import Schema, fields


class BaseSchema(Schema):
    id = fields.Int(dump_only=True)  # 只输出，不接受输入
    created_at = fields.DateTime(dump_only=True, format='%Y-%m-%d %H:%M:%S')
    updated_at = fields.DateTime(dump_only=True, format='%Y-%m-%d %H:%M:%S')


class PaginationSchema(Schema):
    page = fields.Int()
    per_page = fields.Int()
    total = fields.Int()
    pages = fields.Int()
    has_next = fields.Bool()
    has_prev = fields.Bool()


class ResponseSchema(Schema):
    code = fields.Int()
    msg = fields.Str()
    data = fields.Raw()  # 可以是任意类型
