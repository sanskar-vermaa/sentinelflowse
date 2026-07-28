from app.core.security import hash_password
from app.db.init_db import create_all_tables
from app.db.session import SessionLocal
from app.models.incident import Incident, IncidentSeverity, IncidentStatus
from app.models.organization import MemberRole, Organization, OrganizationMembership, User
from app.models.workflow import Workflow


def seed_demo_data() -> None:
    create_all_tables()
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == "admin@sentinelflow.dev").first():
            return

        user = User(
            email="admin@sentinelflow.dev",
            display_name="Demo Admin",
            password_hash=hash_password("sentinelflow-demo"),
        )
        organization = Organization(name="SentinelFlow Demo", slug="sentinelflow-demo")
        membership = OrganizationMembership(user=user, organization=organization, role=MemberRole.owner)
        incident = Incident(
            organization_id=str(organization.id),
            title="Checkout latency above threshold",
            description="Synthetic demo incident for local development.",
            severity=IncidentSeverity.high,
            status=IncidentStatus.open,
            dedupe_key="demo-checkout-latency",
        )
        workflow = Workflow(
            organization_id=str(organization.id),
            name="Page on critical incident",
            trigger="incident.created",
            definition={"steps": [{"type": "notify", "channel": "on-call"}]},
        )
        db.add_all([user, organization, membership, incident, workflow])
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()

