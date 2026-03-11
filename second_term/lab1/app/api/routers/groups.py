from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api import crud
from app.api.schemas import (
    GroupCreate,
    GroupUpdate,
    GroupRead,
)
from app.core.auth import get_current_user
from app.core.common import list_params, ListParams
from app.db.db import get_db

router = APIRouter(prefix="/groups", tags=["groups"])


@router.get("", response_model=list[GroupRead])
def list_groups(
    db: Session = Depends(get_db),
    params: ListParams = Depends(list_params),
    name: str | None = Query(None),
    university_id: int | None = Query(None),
    course: int | None = Query(None, ge=1, le=6),
    admission_year: int | None = Query(None, ge=1990, le=2100),
    user=Depends(get_current_user),
):
    return crud.list_groups(db, params, name, university_id, course, admission_year)


@router.get("/{group_id}", response_model=GroupRead)
def get_group(
    group_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_group(db, group_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Group not found")
    return obj


@router.post("", response_model=GroupRead, status_code=status.HTTP_201_CREATED)
def create_group(
    payload: GroupCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return crud.create_group(db, payload)
    except ValueError as e:
        if str(e) == "university_not_found":
            raise HTTPException(status_code=404, detail="University not found")
        raise
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Group with this name/year already exists in this university")


@router.put("/{group_id}", response_model=GroupRead)
def update_group(
    group_id: int,
    payload: GroupUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_group(db, group_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Group not found")
    try:
        return crud.update_group(db, obj, payload)
    except ValueError as e:
        if str(e) == "university_not_found":
            raise HTTPException(status_code=404, detail="University not found")
        raise
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflict while updating group")


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
    group_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_group(db, group_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Group not found")
    crud.delete_group(db, obj)
    return None
