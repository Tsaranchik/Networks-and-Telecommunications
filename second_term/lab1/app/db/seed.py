from dotenv import load_dotenv
load_dotenv()

from app.core.auth import hash_password

from decimal import Decimal

from app.db.db import SessionLocal
from app.db.models import (
    ScholarshipType,
    University,
    UniversityCoeff,
    Group,
    Student,
    ScholarshipAssignment,
    User
)

def get_or_create(db, model, defaults=None, **kwargs):
    obj = db.query(model).filter_by(**kwargs).first()
    if obj:
        return obj, False
    params = dict(kwargs)
    if defaults:
        params.update(defaults)
    obj = model(**params)
    db.add(obj)
    db.flush()  # чтобы получить obj.id
    return obj, True


def main():
    db = SessionLocal()
    try:
        # 1) Scholarship types
        st_norm, _ = get_or_create(
            db, ScholarshipType,
            name="обычная",
            defaults={"base_amount": Decimal("3000.00")}
        )
        st_high, _ = get_or_create(
            db, ScholarshipType,
            name="повышенная",
            defaults={"base_amount": Decimal("6000.00")}
        )
        st_soc, _ = get_or_create(
            db, ScholarshipType,
            name="социальная",
            defaults={"base_amount": Decimal("4500.00")}
        )

        # 2) Universities
        u1, _ = get_or_create(db, University, name="Университет А")
        u2, _ = get_or_create(db, University, name="Университет Б")

        # 3) Coeffs (для каждой пары вуз+тип)
        def upsert_coeff(univ, stype, coeff: str):
            obj = (
                db.query(UniversityCoeff)
                .filter_by(university_id=univ.id, scholarship_type_id=stype.id)
                .first()
            )
            if obj:
                obj.coeff = Decimal(coeff)
                return obj
            obj = UniversityCoeff(
                university_id=univ.id,
                scholarship_type_id=stype.id,
                coeff=Decimal(coeff),
            )
            db.add(obj)
            return obj

        # Университет А
        upsert_coeff(u1, st_norm, "1.00")
        upsert_coeff(u1, st_high, "1.10")
        upsert_coeff(u1, st_soc,  "0.95")

        # Университет Б
        upsert_coeff(u2, st_norm, "1.15")
        upsert_coeff(u2, st_high, "1.25")
        upsert_coeff(u2, st_soc,  "1.05")

        # 4) Groups
        g1, _ = get_or_create(
            db, Group,
            university_id=u1.id,
            name="ИКБО-10-23",
            admission_year=2023,
            defaults={
                "course": 3,
                "curator_full_name": "Иванов Иван Иванович",
                "curator_photo": None,
            },
        )

        g2, _ = get_or_create(
            db, Group,
            university_id=u2.id,
            name="ПИ-01-24",
            admission_year=2024,
            defaults={
                "course": 2,
                "curator_full_name": "Петров Пётр Петрович",
                "curator_photo": "https://example.com/curator.jpg",
            },
        )

        # 5) Students
        s1, _ = get_or_create(
            db, Student,
            full_name="Сидоров Сергей Сергеевич",
            group_id=g1.id,
            defaults={"address": "г. Москва, ул. Пример, д. 1"},
        )
        s2, _ = get_or_create(
            db, Student,
            full_name="Кузнецова Анна Андреевна",
            group_id=g1.id,
            defaults={"address": "г. Москва, ул. Тестовая, д. 2"},
        )
        s3, _ = get_or_create(
            db, Student,
            full_name="Смирнов Алексей Алексеевич",
            group_id=g2.id,
            defaults={"address": "г. Казань, пр-т Учебный, д. 3"},
        )

        # 6) Scholarship assignments (семестр + вычисление amount)
        def compute_amount(student: Student, stype: ScholarshipType) -> Decimal:
            # вуз через student -> group
            group = db.query(Group).filter_by(id=student.group_id).one()
            coeff = (
                db.query(UniversityCoeff)
                .filter_by(university_id=group.university_id, scholarship_type_id=stype.id)
                .one()
            )
            return (stype.base_amount * coeff.coeff).quantize(Decimal("0.01"))

        def upsert_assignment(student: Student, semester: int, stype: ScholarshipType):
            obj = (
                db.query(ScholarshipAssignment)
                .filter_by(student_id=student.id, semester=semester)
                .first()
            )
            amount = compute_amount(student, stype)
            if obj:
                obj.scholarship_type_id = stype.id
                obj.amount = amount
                return obj
            obj = ScholarshipAssignment(
                student_id=student.id,
                semester=semester,
                scholarship_type_id=stype.id,
                amount=amount,
            )
            db.add(obj)
            return obj

        upsert_assignment(s1, 1, st_norm)
        upsert_assignment(s1, 2, st_high)
        upsert_assignment(s2, 1, st_soc)
        upsert_assignment(s3, 1, st_norm)

        admin = db.query(User).filter_by(username="admin").first()
        if not admin:
            admin = User(username="admin", hashed_password=hash_password("admin"), is_active=True)
            db.add(admin)

        db.commit()
        print("Seed done ✅")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

