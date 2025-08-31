from apiflask import APIBlueprint

# 创建API v1蓝图
bp = APIBlueprint('v1', __name__)

# 导入所有路由模块（自动注册路由）
from . import users
