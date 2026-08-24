from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_membership
from app.core.rbac import Permission, has_permission
from app.db import get_db
from app.models.organization import User
from app.schemas.workflows import WorkflowCreate, WorkflowRead, WorkflowRunRead
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

