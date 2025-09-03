from apiflask import APIBlueprint

users_bp = APIBlueprint('users', __name__, tag='Users')
auth_bp = APIBlueprint('auth', __name__, tag='Authentication')

from . import users, auth
