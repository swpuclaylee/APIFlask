from apiflask import APIBlueprint

users_bp = APIBlueprint('users', __name__, tag='Users')
auth_bp = APIBlueprint('auth', __name__, tag='Authentication')
roles_bp = APIBlueprint('roles', __name__, tag='Roles')

from . import users, auth
