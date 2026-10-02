from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership
from app.core.config import settings
from app.core.rbac import Permission, has_permission
from app.db import get_db
from app.models.organization import User
from app.schemas.workflows import (
    WorkflowCreate,
    WorkflowRead,
    WorkflowRunCreate,
    WorkflowRunRead,
    WorkflowUpdate,
)
from app.services.incident_service import IncidentService
from app.services.workflow_engine import (
    InvalidDefinition,
    WorkflowEngine,
    validate_definition,
)
from app.services.workflow_service import WorkflowService

router = APIRouter(prefix="/organizations/{organization_id}/workflows", tags=["workflows"])


@router.get("", response_model=list[WorkflowRead])
def list_workflows(
    organization_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[WorkflowRead]:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_read):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing read permission")
    workflows = WorkflowService(db).list_workflows(organization_id)
    return [WorkflowRead.model_validate(workflow, from_attributes=True) for workflow in workflows]


@router.post("", response_model=WorkflowRead, status_code=status.HTTP_201_CREATED)
def create_workflow(
    organization_id: UUID,
    request: WorkflowCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkflowRead:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.workflow_manage):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing workflow manage permission")
    try:
        validate_definition(request.trigger, request.definition)
    except InvalidDefinition as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from None
    workflow = WorkflowService(db).create_workflow(organization_id, request)
    return WorkflowRead.model_validate(workflow, from_attributes=True)


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(
    organization_id: UUID,
    workflow_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkflowRead:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_read):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing read permission")
    workflow = WorkflowService(db).get_workflow(organization_id, workflow_id)
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return WorkflowRead.model_validate(workflow, from_attributes=True)


@router.get("/{workflow_id}/runs", response_model=list[WorkflowRunRead])
def list_workflow_runs(
    organization_id: UUID,
    workflow_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> list[WorkflowRunRead]:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.incident_read):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing read permission")
    service = WorkflowService(db)
    if service.get_workflow(organization_id, workflow_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    runs = service.list_runs(workflow_id)
    return [WorkflowRunRead.model_validate(run, from_attributes=True) for run in runs]



@router.patch("/{workflow_id}", response_model=WorkflowRead)
def update_workflow(
    organization_id: UUID,
    workflow_id: UUID,
    request: WorkflowUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkflowRead:
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.workflow_manage):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing workflow manage permission")
    workflow = WorkflowService(db).get_workflow(organization_id, workflow_id)
    if workflow is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if request.name is not None:
        workflow.name = request.name
    if request.is_enabled is not None:
        workflow.is_enabled = request.is_enabled
    db.commit()
    db.refresh(workflow)
    return WorkflowRead.model_validate(workflow, from_attributes=True)


@router.post("/{workflow_id}/runs", response_model=WorkflowRunRead, status_code=status.HTTP_202_ACCEPTED)
def run_workflow(
    organization_id: UUID,
    workflow_id: UUID,
    request: WorkflowRunCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
) -> WorkflowRunRead:
    """Queue a manual run, optionally against an incident in the same organization."""
    membership = get_membership(db, current_user.id, organization_id)
    if not has_permission(membership, Permission.workflow_manage):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Missing workflow manage permission")
    service = WorkflowService(db)
    if service.get_workflow(organization_id, workflow_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    if request.incident_id is not None and IncidentService(db).get_incident(organization_id, request.incident_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident not found")

    run = service.create_run(workflow_id, request.incident_id, {"event": "manual", "actor_id": str(current_user.id)})
    if settings.workflow_execution == "inline":
        run = WorkflowEngine(db).execute(run)
    return WorkflowRunRead.model_validate(run, from_attributes=True)
