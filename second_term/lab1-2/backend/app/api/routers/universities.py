from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api import crud
from app.api.schemas import (
    UniversityCreate,
    UniversityUpdate,
    UniversityRead,
)
from app.core.auth import get_current_user
from app.core.common import list_params, ListParams, set_pagination_headers
from app.db.db import get_db

router = APIRouter(prefix="/universities", tags=["universities"])


@router.get("", response_model=list[UniversityRead])
def list_universities(
    response: Response,
    db: Session = Depends(get_db),
    params: ListParams = Depends(list_params),
    item_id: int | None = Query(None, alias="id"),
    name: str | None = Query(None),
):
    items, total = crud.list_universities(db, params, item_id, name)
    set_pagination_headers(response, params, total)
    return items


@router.get("/{univ_id}", response_model=UniversityRead)
def get_university(univ_id: int, db: Session = Depends(get_db)):
    obj = crud.get_university(db, univ_id)
    if not obj:
        raise HTTPException(status_code=404, detail="University not found")
    return obj


@router.post("", response_model=UniversityRead, status_code=status.HTTP_201_CREATED)
def create_university(
    payload: UniversityCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return crud.create_university(db, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="University with this name already exists")


@router.put("/{univ_id}", response_model=UniversityRead)
def update_university(
    univ_id: int,
    payload: UniversityUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_university(db, univ_id)
    if not obj:
        raise HTTPException(status_code=404, detail="University not found")
    try:
        return crud.update_university(db, obj, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="University with this name already exists")


@router.delete("/{univ_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_university(
    univ_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_university(db, univ_id)
    if not obj:
        raise HTTPException(status_code=404, detail="University not found")
    crud.delete_university(db, obj)
    return None
