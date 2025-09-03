from app import db
from app.models.permission import Permission
from app.models.role import Role
from app.models.user import User
from app.utils.permissions import Permissions, Roles


class RBACInitService:
    """RBAC系统初始化服务"""

    @staticmethod
    def init_permissions():
        """初始化基础权限"""
        # 使用权限常量定义权限数据
        permissions_data = [
            # 格式: (权限名称, 描述, 资源, 操作)
            (Permissions.USER_CREATE, '创建用户', 'user', 'create'),
            (Permissions.USER_READ, '查看用户', 'user', 'read'),
            (Permissions.USER_UPDATE, '更新用户', 'user', 'update'),
            (Permissions.USER_DELETE, '删除用户', 'user', 'delete'),

            (Permissions.ROLE_CREATE, '创建角色', 'role', 'create'),
            (Permissions.ROLE_READ, '查看角色', 'role', 'read'),
            (Permissions.ROLE_UPDATE, '更新角色', 'role', 'update'),
            (Permissions.ROLE_DELETE, '删除角色', 'role', 'delete'),

            (Permissions.PERMISSION_CREATE, '创建权限', 'permission', 'create'),
            (Permissions.PERMISSION_READ, '查看权限', 'permission', 'read'),
            (Permissions.PERMISSION_UPDATE, '更新权限', 'permission', 'update'),
            (Permissions.PERMISSION_DELETE, '删除权限', 'permission', 'delete'),

            (Permissions.ORDER_CREATE, '创建订单', 'order', 'create'),
            (Permissions.ORDER_READ, '查看订单', 'order', 'read'),
            (Permissions.ORDER_UPDATE, '更新订单', 'order', 'update'),
            (Permissions.ORDER_DELETE, '删除订单', 'order', 'delete'),

            (Permissions.PRODUCT_CREATE, '创建产品', 'product', 'create'),
            (Permissions.PRODUCT_READ, '查看产品', 'product', 'read'),
            (Permissions.PRODUCT_UPDATE, '更新产品', 'product', 'update'),
            (Permissions.PRODUCT_DELETE, '删除产品', 'product', 'delete'),

            (Permissions.REPORT_READ, '查看报告', 'report', 'read'),
            (Permissions.REPORT_MANAGE, '管理报告', 'report', 'manage'),

            (Permissions.SYSTEM_CONFIG, '系统配置', 'system', 'config'),
            (Permissions.SYSTEM_LOG, '查看日志', 'system', 'log'),
        ]

        for name, description, resource, action in permissions_data:
            # 检查权限是否已存在
            existing = Permission.query.filter_by(name=name).first()
            if not existing:
                perm = Permission(
                    name=name,
                    description=description,
                    resource=resource,
                    action=action
                )
                db.session.add(perm)

        db.session.commit()
        print("基础权限初始化完成")

    @staticmethod
    def init_roles():
        """初始化基础角色并分配权限"""
        # 定义角色和对应的权限 - 这里是权限分配的核心逻辑！
        roles_permissions = {
            # 超级管理员 - 拥有所有权限
            Roles.SUPER_ADMIN: {
                'description': '超级管理员，拥有系统所有权限',
                'permissions': Permissions.get_all_permissions()  # 获取所有权限
            },

            # 管理员 - 拥有大部分管理权限
            Roles.ADMIN: {
                'description': '系统管理员，拥有用户、角色、权限管理权限',
                'permissions': [
                    # 用户管理权限
                    Permissions.USER_CREATE, Permissions.USER_READ,
                    Permissions.USER_UPDATE, Permissions.USER_DELETE,

                    # 角色管理权限
                    Permissions.ROLE_CREATE, Permissions.ROLE_READ,
                    Permissions.ROLE_UPDATE, Permissions.ROLE_DELETE,

                    # 权限查看
                    Permissions.PERMISSION_READ,

                    # 系统权限
                    Permissions.SYSTEM_CONFIG, Permissions.SYSTEM_LOG,

                    # 报告权限
                    Permissions.REPORT_READ, Permissions.REPORT_MANAGE
                ]
            },

            # 用户管理员
            Roles.USER_MANAGER: {
                'description': '用户管理员，负责用户相关操作',
                'permissions': [
                    Permissions.USER_CREATE, Permissions.USER_READ, Permissions.USER_UPDATE,
                    Permissions.ROLE_READ,  # 可以查看角色列表
                    Permissions.REPORT_READ
                ]
            },

            # 订单管理员
            Roles.ORDER_MANAGER: {
                'description': '订单管理员，负责订单相关操作',
                'permissions': [
                    # 订单管理权限
                    Permissions.ORDER_CREATE, Permissions.ORDER_READ,
                    Permissions.ORDER_UPDATE, Permissions.ORDER_DELETE,

                    # 相关查看权限
                    Permissions.USER_READ,  # 需要查看用户信息
                    Permissions.PRODUCT_READ,  # 需要查看产品信息
                    Permissions.REPORT_READ
                ]
            },

            # 产品管理员
            Roles.PRODUCT_MANAGER: {
                'description': '产品管理员，负责产品相关操作',
                'permissions': [
                    Permissions.PRODUCT_CREATE, Permissions.PRODUCT_READ,
                    Permissions.PRODUCT_UPDATE, Permissions.PRODUCT_DELETE,
                    Permissions.REPORT_READ
                ]
            },

            # 客服
            Roles.CUSTOMER_SERVICE: {
                'description': '客服人员，处理用户咨询和订单问题',
                'permissions': [
                    Permissions.USER_READ, Permissions.USER_UPDATE,  # 可以查看和更新用户信息
                    Permissions.ORDER_READ, Permissions.ORDER_UPDATE,  # 可以查看和处理订单
                    Permissions.PRODUCT_READ  # 可以查看产品信息
                ]
            },

            # 财务
            Roles.FINANCE: {
                'description': '财务人员，查看相关报告和订单',
                'permissions': [
                    Permissions.ORDER_READ,  # 查看订单（财务相关）
                    Permissions.REPORT_READ,  # 查看报告
                    Permissions.USER_READ  # 查看用户基本信息
                ]
            },

            # 普通用户
            Roles.USER: {
                'description': '普通用户，基本查看权限',
                'permissions': [
                    Permissions.USER_READ,  # 查看自己的信息
                    Permissions.PRODUCT_READ,  # 查看产品
                    Permissions.ORDER_READ  # 查看自己的订单
                ]
            },

            # 访客
            Roles.GUEST: {
                'description': '访客用户，只能查看公开内容',
                'permissions': [
                    Permissions.PRODUCT_READ  # 只能查看产品
                ]
            }
        }

        # 创建角色并分配权限 - 核心权限分配逻辑！
        for role_name, role_data in roles_permissions.items():
            # 检查角色是否已存在
            existing_role = Role.query.filter_by(name=role_name).first()
            if not existing_role:
                # 创建角色
                role = Role(name=role_name, description=role_data['description'])
                db.session.add(role)
                db.session.flush()  # 获取role.id

                # 分配权限 - 这里是关键！
                for perm_name in role_data['permissions']:
                    permission = Permission.query.filter_by(name=perm_name).first()
                    if permission:
                        role.permissions.append(permission)
                    else:
                        print(f"警告: 权限 {perm_name} 不存在")

                print(f"角色 {role_name} 创建完成，分配了 {len(role_data['permissions'])} 个权限")

        db.session.commit()
        print("基础角色初始化完成")

    @staticmethod
    def create_admin_user(username: str = "admin", email: str = "admin@example.com"):
        """创建超级管理员用户"""
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"用户 {username} 已存在")
            return existing_user

        # 创建用户
        admin_user = User(username=username, email=email)
        db.session.add(admin_user)
        db.session.flush()

        # 分配超级管理员角色
        super_admin_role = Role.query.filter_by(name='super_admin').first()
        if super_admin_role:
            admin_user.roles.append(super_admin_role)

        db.session.commit()
        print(f"超级管理员 {username} 创建完成")
        return admin_user

    @staticmethod
    def init_all():
        """初始化所有RBAC数据"""
        print("开始初始化RBAC系统...")
        RBACInitService.init_permissions()
        RBACInitService.init_roles()
        RBACInitService.create_admin_user()
        print("RBAC系统初始化完成！")
