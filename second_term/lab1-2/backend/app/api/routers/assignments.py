from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api import crud
from app.api.schemas import (
    ScholarshipAssignmentCreate,
    ScholarshipAssignmentUpdate,
    ScholarshipAssignmentRead,
)
from app.core.auth import get_current_user
from app.core.common import list_params, ListParams, set_pagination_headers
from app.db.db import get_db

router = APIRouter(prefix="/scholarship-assignments", tags=["scholarship-assignments"])


@router.get("", response_model=list[ScholarshipAssignmentRead])
def list_scholarship_assignments(
    response: Response,
    db: Session = Depends(get_db),
    params: ListParams = Depends(list_params),
    item_id: int | None = Query(None, alias="id"),
    student_id: int | None = Query(None),
    semester: int | None = Query(None, ge=1, le=20),
    scholarship_type_id: int | None = Query(None),
    amount: Decimal | None = Query(None),
    user=Depends(get_current_user),
):
    items, total = crud.list_assignments(
        db, params, item_id, student_id, semester, scholarship_type_id, amount
    )
    set_pagination_headers(response, params, total)
    return items


@router.get("/{assign_id}", response_model=ScholarshipAssignmentRead)
def get_scholarship_assignment(
    assign_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_assignment(db, assign_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Scholarship assignment not found")
    return obj


@router.post("", response_model=ScholarshipAssignmentRead, status_code=status.HTTP_201_CREATED)
def create_scholarship_assignment(
    payload: ScholarshipAssignmentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return crud.create_assignment(db, payload)
    except ValueError as e:
        code = str(e)
        if code == "student_not_found":
            raise HTTPException(status_code=404, detail="Student not found")
        if code == "scholarship_type_not_found":
            raise HTTPException(status_code=404, detail="Scholarship type not found")
        if code == "coeff_not_found":
            raise HTTPException(status_code=409, detail="No coefficient for this university and scholarship type")
        raise
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Scholarship assignment for this student and semester already exists")


@router.put("/{assign_id}", response_model=ScholarshipAssignmentRead)
def update_scholarship_assignment(
    assign_id: int,
    payload: ScholarshipAssignmentUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_assignment(db, assign_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Scholarship assignment not found")
    try:
        return crud.update_assignment(db, obj, payload)
    except ValueError as e:
        code = str(e)
        if code == "student_not_found":
            raise HTTPException(status_code=404, detail="Student not found")
        if code == "scholarship_type_not_found":
            raise HTTPException(status_code=404, detail="Scholarship type not found")
        if code == "coeff_not_found":
            raise HTTPException(status_code=409, detail="No coefficient for this university and scholarship type")
        raise
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflict while updating scholarship assignment")


@router.delete("/{assign_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scholarship_assignment(
    assign_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_assignment(db, assign_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Scholarship assignment not found")
    crud.delete_assignment(db, obj)
    return None
