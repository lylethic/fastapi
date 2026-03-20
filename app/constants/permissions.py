class Permission:
    WRITE = "WRITE"
    VIEW = "VIEW"
    EDIT = "EDIT"
    DELETE = "DELETE"
    SYS_ADMIN = "SYS_ADMIN"


ALL_PERMISSIONS = (
    Permission.WRITE,
    Permission.VIEW,
    Permission.EDIT,
    Permission.DELETE,
    Permission.SYS_ADMIN,
)
