from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select
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
from app.core.common import ListParams, paginate_query


ALLOWED_SORT_FIELDS = {"id", "name", "base_amount", "created_at", "updated_at"}

def list_scholarship_types(
    db: Session,
    params: ListParams,
    item_id: int | None,
    name: str | None,
    base_amount: Decimal | None,
):
    stmt = select(ScholarshipType)
    if item_id is not None:
        stmt = stmt.where(ScholarshipType.id == item_id)
    if name:
        stmt = stmt.where(ScholarshipType.name.ilike(f"%{name}%"))
    if base_amount is not None:
        stmt = stmt.where(ScholarshipType.base_amount == base_amount)

    return paginate_query(db, stmt, ScholarshipType, params, ALLOWED_SORT_FIELDS)


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


UNIV_ALLOWED_SORT_FIELDS = {"id", "name", "created_at", "updated_at"}

def list_universities(
    db: Session,
    params: ListParams,
    item_id: int | None,
    name: str | None,
):
    stmt = select(University)

    if item_id is not None:
        stmt = stmt.where(University.id == item_id)
    if name:
        stmt = stmt.where(University.name.ilike(f"%{name}%"))

    return paginate_query(db, stmt, University, params, UNIV_ALLOWED_SORT_FIELDS)


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


COEFF_ALLOWED_SORT_FIELDS = {
    "id",
    "university_id",
    "scholarship_type_id",
    "coeff",
    "created_at",
    "updated_at",
}

def list_university_coeffs(
    db: Session,
    params: ListParams,
    item_id: int | None,
    university_id: int | None,
    scholarship_type_id: int | None,
    coeff: Decimal | None,
):
    stmt = select(UniversityCoeff).options(
        joinedload(UniversityCoeff.university),
        joinedload(UniversityCoeff.scholarship_type),
    )

    if item_id is not None:
        stmt = stmt.where(UniversityCoeff.id == item_id)
    if university_id is not None:
        stmt = stmt.where(UniversityCoeff.university_id == university_id)
    if scholarship_type_id is not None:
        stmt = stmt.where(UniversityCoeff.scholarship_type_id == scholarship_type_id)
    if coeff is not None:
        stmt = stmt.where(UniversityCoeff.coeff == coeff)

    return paginate_query(db, stmt, UniversityCoeff, params, COEFF_ALLOWED_SORT_FIELDS)


def get_university_coeff(db: Session, coeff_id: int) -> UniversityCoeff | None:
    stmt = (
        select(UniversityCoeff)
        .options(
            joinedload(UniversityCoeff.university),
            joinedload(UniversityCoeff.scholarship_type),
        )
        .where(UniversityCoeff.id == coeff_id)
    )
    return db.execute(stmt).scalars().first()


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



GROUP_ALLOWED_SORT_FIELDS = {
    "id",
    "name",
    "course",
    "admission_year",
    "university_id",
    "curator_full_name",
    "created_at",
    "updated_at",
}

def list_groups(
    db: Session,
    params: ListParams,
    item_id: int | None,
    name: str | None,
    university_id: int | None,
    course: int | None,
    admission_year: int | None,
    curator_full_name: str | None,
):
    stmt = select(Group).options(joinedload(Group.university))

    if item_id is not None:
        stmt = stmt.where(Group.id == item_id)
    if name:
        stmt = stmt.where(Group.name.ilike(f"%{name}%"))
    if university_id is not None:
        stmt = stmt.where(Group.university_id == university_id)
    if course is not None:
        stmt = stmt.where(Group.course == course)
    if admission_year is not None:
        stmt = stmt.where(Group.admission_year == admission_year)
    if curator_full_name:
        stmt = stmt.where(Group.curator_full_name.ilike(f"%{curator_full_name}%"))

    return paginate_query(db, stmt, Group, params, GROUP_ALLOWED_SORT_FIELDS)


def get_group(db: Session, group_id: int) -> Group | None:
    stmt = select(Group).options(joinedload(Group.university)).where(Group.id == group_id)
    return db.execute(stmt).scalars().first()


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
    if "curator_photo" in data.model_fields_set:
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


STUDENT_ALLOWED_SORT_FIELDS = {"id", "full_name", "group_id", "created_at", "updated_at"}

def list_students(
    db: Session,
    params: ListParams,
    item_id: int | None,
    full_name: str | None,
    group_id: int | None,
    address: str | None,
):
    stmt = select(Student).options(joinedload(Student.group))

    if item_id is not None:
        stmt = stmt.where(Student.id == item_id)
    if full_name:
        stmt = stmt.where(Student.full_name.ilike(f"%{full_name}%"))
    if group_id is not None:
        stmt = stmt.where(Student.group_id == group_id)
    if address:
        stmt = stmt.where(Student.address.ilike(f"%{address}%"))

    return paginate_query(db, stmt, Student, params, STUDENT_ALLOWED_SORT_FIELDS)


def get_student(db: Session, student_id: int) -> Student | None:
    stmt = select(Student).options(joinedload(Student.group)).where(Student.id == student_id)
    return db.execute(stmt).scalars().first()


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


ASSIGN_ALLOWED_SORT_FIELDS = {
    "id",
    "student_id",
    "semester",
    "scholarship_type_id",
    "amount",
    "created_at",
    "updated_at",
}

def list_assignments(
    db: Session,
    params: ListParams,
    item_id: int | None,
    student_id: int | None,
    semester: int | None,
    scholarship_type_id: int | None,
    amount: Decimal | None,
):
    stmt = select(ScholarshipAssignment).options(
        joinedload(ScholarshipAssignment.student).joinedload(Student.group),
        joinedload(ScholarshipAssignment.scholarship_type),
    )

    if item_id is not None:
        stmt = stmt.where(ScholarshipAssignment.id == item_id)
    if student_id is not None:
        stmt = stmt.where(ScholarshipAssignment.student_id == student_id)
    if semester is not None:
        stmt = stmt.where(ScholarshipAssignment.semester == semester)
    if scholarship_type_id is not None:
        stmt = stmt.where(ScholarshipAssignment.scholarship_type_id == scholarship_type_id)
    if amount is not None:
        stmt = stmt.where(ScholarshipAssignment.amount == amount)

    return paginate_query(db, stmt, ScholarshipAssignment, params, ASSIGN_ALLOWED_SORT_FIELDS)


def get_assignment(db: Session, assign_id: int) -> ScholarshipAssignment | None:
    stmt = (
        select(ScholarshipAssignment)
        .options(
            joinedload(ScholarshipAssignment.student).joinedload(Student.group),
            joinedload(ScholarshipAssignment.scholarship_type),
        )
        .where(ScholarshipAssignment.id == assign_id)
    )
    return db.execute(stmt).scalars().first()


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
