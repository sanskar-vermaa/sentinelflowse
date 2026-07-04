from types import SimpleNamespace

from app.core.rbac import Permission, has_permission
from app.models.organization import MemberRole


def test_owner_has_all_permissions() -> None:
    membership = SimpleNamespace(role=MemberRole.owner)

    assert has_permission(membership, Permission.organization_manage)
    assert has_permission(membership, Permission.workflow_manage)


def test_viewer_can_only_read_incidents() -> None:
    membership = SimpleNamespace(role=MemberRole.viewer)

    assert has_permission(membership, Permission.incident_read)
    assert not has_permission(membership, Permission.incident_assign)

