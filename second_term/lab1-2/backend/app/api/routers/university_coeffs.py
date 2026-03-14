from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api import crud
from app.api.schemas import (
    UniversityCoeffCreate,
    UniversityCoeffUpdate,
    UniversityCoeffRead,
)
from app.core.auth import get_current_user
from app.core.common import list_params, ListParams, set_pagination_headers
from app.db.db import get_db

router = APIRouter(prefix="/university-coeffs", tags=["university-coeffs"])


@router.get("", response_model=list[UniversityCoeffRead])
def list_university_coeffs(
    response: Response,
    db: Session = Depends(get_db),
    params: ListParams = Depends(list_params),
    item_id: int | None = Query(None, alias="id"),
    university_id: int | None = Query(None),
    scholarship_type_id: int | None = Query(None),
    coeff: Decimal | None = Query(None),
):
    items, total = crud.list_university_coeffs(
        db, params, item_id, university_id, scholarship_type_id, coeff
    )
    set_pagination_headers(response, params, total)
    return items


@router.get("/{coeff_id}", response_model=UniversityCoeffRead)
def get_university_coeff(coeff_id: int, db: Session = Depends(get_db)):
    obj = crud.get_university_coeff(db, coeff_id)
    if not obj:
        raise HTTPException(status_code=404, detail="University coeff not found")
    return obj


@router.post("", response_model=UniversityCoeffRead, status_code=status.HTTP_201_CREATED)
def create_university_coeff(
    payload: UniversityCoeffCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    try:
        return crud.create_university_coeff(db, payload)
    except ValueError as e:
        if str(e) == "university_not_found":
            raise HTTPException(status_code=404, detail="University not found")
        if str(e) == "scholarship_type_not_found":
            raise HTTPException(status_code=404, detail="Scholarship type not found")
        raise
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Coeff for this university and scholarship type already exists")


@router.put("/{coeff_id}", response_model=UniversityCoeffRead)
def update_university_coeff(
    coeff_id: int,
    payload: UniversityCoeffUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_university_coeff(db, coeff_id)
    if not obj:
        raise HTTPException(status_code=404, detail="University coeff not found")
    try:
        return crud.update_university_coeff(db, obj, payload)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Conflict while updating coeff")


@router.delete("/{coeff_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_university_coeff(
    coeff_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    obj = crud.get_university_coeff(db, coeff_id)
    if not obj:
        raise HTTPException(status_code=404, detail="University coeff not found")
    crud.delete_university_coeff(db, obj)
    return None
