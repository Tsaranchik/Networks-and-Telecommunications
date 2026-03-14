from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api import crud
from app.api.schemas import (
    StudentCreate,
    StudentUpdate,
    StudentRead,
)
from app.core.auth import get_current_user
from app.core.common import list_params, ListParams, set_pagination_headers
from app.db.db import get_db

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentRead])
def list_students(
    response: Response,
    db: Session = Depends(get_db),
    params: ListParams = Depends(list_params),
    item_id: int | None = Query(None, alias="id"),
    full_name: str | None = Query(None, description="Filter by full name (contains, case-insensitive)"),
    group_id: int | None = Query(None),
    address: str | None = Query(None),
    user=Depends(get_current_user),
):
    items, total = crud.list_students(db, params, item_id, full_name, group_id, address)
    set_pagination_headers(response, params, total)
    return items


@router.get("/{student_id}", response_model=StudentRead)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_student(db, student_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Student not found")
    return obj


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(
    payload: StudentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return crud.create_student(db, payload)
    except ValueError as e:
        if str(e) == "group_not_found":
            raise HTTPException(status_code=404, detail="Group not found")
        raise


@router.put("/{student_id}", response_model=StudentRead)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_student(db, student_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Student not found")
    try:
        return crud.update_student(db, obj, payload)
    except ValueError as e:
        if str(e) == "group_not_found":
            raise HTTPException(status_code=404, detail="Group not found")
        raise


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_student(db, student_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Student not found")
    crud.delete_student(db, obj)
    return None
