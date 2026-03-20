class Permission:
    CREATE = "CREATE"
    VIEW = "VIEW"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    SYS_ADMIN = "SYS_ADMIN"


ALL_PERMISSIONS = (
    Permission.CREATE,
    Permission.VIEW,
    Permission.UPDATE,
    Permission.DELETE,
    Permission.SYS_ADMIN,
)
