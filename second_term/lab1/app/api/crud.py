from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc
from sqlalchemy.exc import IntegrityError

from decimal import Decimal

from app.db.models import (
	ScholarshipType,
	University,
	UniversityCoeff,
	Group,
	Student,
	ScholarshipAssignment
)
from app.api.schemas import ScholarshipTypeCreate, ScholarshipTypeUpdate
from app.core.common import ListParams, apply_list_params


ALLOWED_SORT_FIELDS = {"id", "name", "base_amount"}

def list_scholarship_types(db: Session, params: ListParams, name: str | None):
    stmt = select(ScholarshipType)
    if name:
        stmt = stmt.where(ScholarshipType.name.ilike(f"%{name}%"))

    stmt = apply_list_params(stmt, ScholarshipType, params, ALLOWED_SORT_FIELDS)
    return db.execute(stmt).scalars().all()


def get_scholarship_type(db: Session, st_id: int) -> ScholarshipType | None:
    return db.get(ScholarshipType, st_id)


def create_scholarship_type(db: Session, data: ScholarshipTypeCreate) -> ScholarshipType:
    obj = ScholarshipType(name=data.name, base_amount=data.base_amount)
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def update_scholarship_type(db: Session, obj: ScholarshipType, data: ScholarshipTypeUpdate) -> ScholarshipType:
    if data.name is not None:
        obj.name = data.name
    if data.base_amount is not None:
        obj.base_amount = data.base_amount

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def delete_scholarship_type(db: Session, obj: ScholarshipType) -> None:
    db.delete(obj)
    db.commit()


UNIV_ALLOWED_SORT_FIELDS = {"id", "name"}

def list_universities(db: Session, params: ListParams, name: str | None):
    stmt = select(University)

    if name:
        stmt = stmt.where(University.name.ilike(f"%{name}%"))

    stmt = apply_list_params(stmt, University, params, UNIV_ALLOWED_SORT_FIELDS)
    return db.execute(stmt).scalars().all()


def get_university(db: Session, univ_id: int) -> University | None:
    return db.get(University, univ_id)


def create_university(db: Session, data):
    obj = University(name=data.name)
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def update_university(db: Session, obj: University, data):
    if data.name is not None:
        obj.name = data.name
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def delete_university(db: Session, obj: University) -> None:
    db.delete(obj)
    db.commit()


COEFF_ALLOWED_SORT_FIELDS = {"id", "university_id", "scholarship_type_id", "coeff"}

def list_university_coeffs(
    db: Session,
    params: ListParams,
    university_id: int | None,
    scholarship_type_id: int | None,
):
    stmt = select(UniversityCoeff)

    if university_id is not None:
        stmt = stmt.where(UniversityCoeff.university_id == university_id)
    if scholarship_type_id is not None:
        stmt = stmt.where(UniversityCoeff.scholarship_type_id == scholarship_type_id)

    stmt = apply_list_params(stmt, UniversityCoeff, params, COEFF_ALLOWED_SORT_FIELDS)
    return db.execute(stmt).scalars().all()


def get_university_coeff(db: Session, coeff_id: int) -> UniversityCoeff | None:
    return db.get(UniversityCoeff, coeff_id)


def create_university_coeff(db: Session, data):
    # Проверяем, что FK-объекты существуют (чтобы давать 404, а не “IntegrityError непонятно где”)
    if not db.get(University, data.university_id):
        raise ValueError("university_not_found")
    if not db.get(ScholarshipType, data.scholarship_type_id):
        raise ValueError("scholarship_type_not_found")

    obj = UniversityCoeff(
        university_id=data.university_id,
        scholarship_type_id=data.scholarship_type_id,
        coeff=data.coeff,
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def update_university_coeff(db: Session, obj: UniversityCoeff, data):
    if data.coeff is not None:
        obj.coeff = data.coeff
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def delete_university_coeff(db: Session, obj: UniversityCoeff) -> None:
    db.delete(obj)
    db.commit()



GROUP_ALLOWED_SORT_FIELDS = {"id", "name", "course", "admission_year", "university_id"}

def list_groups(
    db: Session,
    params: ListParams,
    name: str | None,
    university_id: int | None,
    course: int | None,
    admission_year: int | None,
):
    stmt = select(Group)

    if name:
        stmt = stmt.where(Group.name.ilike(f"%{name}%"))
    if university_id is not None:
        stmt = stmt.where(Group.university_id == university_id)
    if course is not None:
        stmt = stmt.where(Group.course == course)
    if admission_year is not None:
        stmt = stmt.where(Group.admission_year == admission_year)

    stmt = apply_list_params(stmt, Group, params, GROUP_ALLOWED_SORT_FIELDS)
    return db.execute(stmt).scalars().all()


def get_group(db: Session, group_id: int) -> Group | None:
    return db.get(Group, group_id)


def create_group(db: Session, data):
    # FK existence check
    if not db.get(University, data.university_id):
        raise ValueError("university_not_found")

    obj = Group(
        name=data.name,
        course=data.course,
        admission_year=data.admission_year,
        university_id=data.university_id,
        curator_full_name=data.curator_full_name,
        curator_photo=data.curator_photo,
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def update_group(db: Session, obj: Group, data):
    if data.university_id is not None:
        if not db.get(University, data.university_id):
            raise ValueError("university_not_found")
        obj.university_id = data.university_id

    if data.name is not None:
        obj.name = data.name
    if data.course is not None:
        obj.course = data.course
    if data.admission_year is not None:
        obj.admission_year = data.admission_year
    if data.curator_full_name is not None:
        obj.curator_full_name = data.curator_full_name
    if data.curator_photo is not None:
        obj.curator_photo = data.curator_photo

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def delete_group(db: Session, obj: Group) -> None:
    db.delete(obj)
    db.commit()


STUDENT_ALLOWED_SORT_FIELDS = {"id", "full_name", "group_id"}

def list_students(
    db: Session,
    params: ListParams,
    full_name: str | None,
    group_id: int | None,
):
    stmt = select(Student)

    if full_name:
        stmt = stmt.where(Student.full_name.ilike(f"%{full_name}%"))
    if group_id is not None:
        stmt = stmt.where(Student.group_id == group_id)

    stmt = apply_list_params(stmt, Student, params, STUDENT_ALLOWED_SORT_FIELDS)
    return db.execute(stmt).scalars().all()


def get_student(db: Session, student_id: int) -> Student | None:
    return db.get(Student, student_id)


def create_student(db: Session, data):
    if not db.get(Group, data.group_id):
        raise ValueError("group_not_found")

    obj = Student(
        full_name=data.full_name,
        group_id=data.group_id,
        address=data.address,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update_student(db: Session, obj: Student, data):
    if data.group_id is not None:
        if not db.get(Group, data.group_id):
            raise ValueError("group_not_found")
        obj.group_id = data.group_id

    if data.full_name is not None:
        obj.full_name = data.full_name
    if data.address is not None:
        obj.address = data.address

    db.commit()
    db.refresh(obj)
    return obj


def delete_student(db: Session, obj: Student) -> None:
    db.delete(obj)
    db.commit()


def _compute_amount(db: Session, student_id: int, scholarship_type_id: int) -> Decimal:
    student = db.get(Student, student_id)
    if not student:
        raise ValueError("student_not_found")

    group = db.get(Group, student.group_id)
    if not group:
        # по идее такого быть не должно, но пусть будет корректно
        raise ValueError("group_not_found")

    stype = db.get(ScholarshipType, scholarship_type_id)
    if not stype:
        raise ValueError("scholarship_type_not_found")

    coeff = (
        db.query(UniversityCoeff)
        .filter_by(university_id=group.university_id, scholarship_type_id=stype.id)
        .first()
    )
    if not coeff:
        raise ValueError("coeff_not_found")

    amount = (stype.base_amount * coeff.coeff).quantize(Decimal("0.01"))
    return amount


ASSIGN_ALLOWED_SORT_FIELDS = {"id", "student_id", "semester", "scholarship_type_id", "amount"}

def list_assignments(
    db: Session,
    params: ListParams,
    student_id: int | None,
    semester: int | None,
    scholarship_type_id: int | None,
):
    stmt = select(ScholarshipAssignment)

    if student_id is not None:
        stmt = stmt.where(ScholarshipAssignment.student_id == student_id)
    if semester is not None:
        stmt = stmt.where(ScholarshipAssignment.semester == semester)
    if scholarship_type_id is not None:
        stmt = stmt.where(ScholarshipAssignment.scholarship_type_id == scholarship_type_id)

    stmt = apply_list_params(stmt, ScholarshipAssignment, params, ASSIGN_ALLOWED_SORT_FIELDS)
    return db.execute(stmt).scalars().all()


def get_assignment(db: Session, assign_id: int) -> ScholarshipAssignment | None:
    return db.get(ScholarshipAssignment, assign_id)


def create_assignment(db: Session, data):
    amount = _compute_amount(db, data.student_id, data.scholarship_type_id)

    obj = ScholarshipAssignment(
        student_id=data.student_id,
        semester=data.semester,
        scholarship_type_id=data.scholarship_type_id,
        amount=amount,
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def update_assignment(db: Session, obj: ScholarshipAssignment, data):
    new_semester = obj.semester if data.semester is None else data.semester
    new_type_id = obj.scholarship_type_id if data.scholarship_type_id is None else data.scholarship_type_id

    # пересчитываем amount, если менялся тип или просто пересчитываем всегда (проще и надёжнее)
    amount = _compute_amount(db, obj.student_id, new_type_id)

    obj.semester = new_semester
    obj.scholarship_type_id = new_type_id
    obj.amount = amount

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(obj)
    return obj


def delete_assignment(db: Session, obj: ScholarshipAssignment) -> None:
    db.delete(obj)
    db.commit()
