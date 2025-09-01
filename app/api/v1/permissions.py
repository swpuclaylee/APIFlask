

@app.get('/permissions')
@require_permission(Permissions.PERMISSION_READ)
def get_all_permissions_api():
    """获取所有权限列表 - 需要权限查看权限"""
    permissions = Permission.query.filter_by(is_active=True).all()
    return {
        "permissions": [
            {
                "id": perm.id,
                "name": perm.name,
                "description": perm.description,
                "resource": perm.resource,
                "action": perm.action
            } for perm in permissions
        ]
    }