from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api import crud
from app.api.schemas import (
    ScholarshipTypeCreate,
    ScholarshipTypeUpdate,
    ScholarshipTypeRead,
)
from app.core.auth import get_current_user
from app.core.common import list_params, ListParams
from app.db.db import get_db

router = APIRouter(prefix="/scholarship-types", tags=["scholarship-types"])


@router.get("", response_model=list[ScholarshipTypeRead])
def list_scholarship_types(
    db: Session = Depends(get_db),
    params: ListParams = Depends(list_params),
    name: str | None = Query(None, description="Filter by name (contains, case-insensitive)"),
):
    return crud.list_scholarship_types(db, params, name)


@router.get("/{st_id}", response_model=ScholarshipTypeRead)
def get_scholarship_type(st_id: int, db: Session = Depends(get_db)):
    obj = crud.get_scholarship_type(db, st_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Scholarship type not found")
    return obj


@router.post("", response_model=ScholarshipTypeRead, status_code=status.HTTP_201_CREATED)
def create_scholarship_type(
    payload: ScholarshipTypeCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return crud.create_scholarship_type(db, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Scholarship type with this name already exists")


@router.put("/{st_id}", response_model=ScholarshipTypeRead)
def update_scholarship_type(
    st_id: int,
    payload: ScholarshipTypeUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_scholarship_type(db, st_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Scholarship type not found")
    try:
        return crud.update_scholarship_type(db, obj, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Scholarship type with this name already exists")


@router.delete("/{st_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scholarship_type(
    st_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_scholarship_type(db, st_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Scholarship type not found")
    crud.delete_scholarship_type(db, obj)
    return None
