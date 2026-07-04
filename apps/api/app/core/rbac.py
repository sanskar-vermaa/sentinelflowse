from enum import StrEnum

from app.models.organization import MemberRole, OrganizationMembership


class Permission(StrEnum):
    incident_read = "incident:read"
    incident_write = "incident:write"
    incident_assign = "incident:assign"
    workflow_manage = "workflow:manage"
    organization_manage = "organization:manage"


ROLE_PERMISSIONS: dict[MemberRole, set[Permission]] = {
    MemberRole.owner: set(Permission),
    MemberRole.admin: {
        Permission.incident_read,
        Permission.incident_write,
        Permission.incident_assign,
        Permission.workflow_manage,
    },
    MemberRole.responder: {
        Permission.incident_read,
        Permission.incident_write,
        Permission.incident_assign,
    },
    MemberRole.viewer: {Permission.incident_read},
}


def has_permission(membership: OrganizationMembership | None, permission: Permission) -> bool:
    if membership is None:
        return False
    return permission in ROLE_PERMISSIONS[membership.role]


def require_permission(membership: OrganizationMembership | None, permission: Permission) -> None:
    if not has_permission(membership, permission):
        raise PermissionError(f"Missing permission: {permission.value}")

