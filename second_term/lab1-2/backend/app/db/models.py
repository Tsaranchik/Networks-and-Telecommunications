from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import (
    String,
    Text,
    Integer,
    ForeignKey,
    UniqueConstraint,
    Numeric,
    DateTime,
    func,
    Boolean
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    default_page_size: Mapped[int] = mapped_column(Integer, nullable=False, server_default="20")
    auto_refresh_seconds: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    default_language: Mapped[str] = mapped_column(String(2), nullable=False, server_default="ru")
    token_version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    @property
    def full_name(self) -> str:
        return " ".join(part for part in [self.last_name, self.first_name, self.middle_name] if part)


class ScholarshipType(Base, TimestampMixin):
    __tablename__ = "scholarship_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # "повышенная", ...
    base_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    coeffs: Mapped[List["UniversityCoeff"]] = relationship(
        back_populates="scholarship_type", cascade="all, delete-orphan"
    )
    assignments: Mapped[List["ScholarshipAssignment"]] = relationship(
        back_populates="scholarship_type"
    )


class University(Base, TimestampMixin):
    __tablename__ = "universities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    coeffs: Mapped[List["UniversityCoeff"]] = relationship(
        back_populates="university", cascade="all, delete-orphan"
    )
    groups: Mapped[List["Group"]] = relationship(
        back_populates="university", cascade="all, delete-orphan"
    )


class UniversityCoeff(Base, TimestampMixin):
    __tablename__ = "university_coeffs"
    __table_args__ = (
        UniqueConstraint("university_id", "scholarship_type_id", name="uq_univ_type_coeff"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id", ondelete="CASCADE"), nullable=False)
    scholarship_type_id: Mapped[int] = mapped_column(ForeignKey("scholarship_types.id", ondelete="CASCADE"), nullable=False)
    coeff: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)

    university: Mapped["University"] = relationship(back_populates="coeffs")
    scholarship_type: Mapped["ScholarshipType"] = relationship(back_populates="coeffs")

    @property
    def university_name(self) -> str | None:
        return self.university.name if self.university else None

    @property
    def scholarship_type_name(self) -> str | None:
        return self.scholarship_type.name if self.scholarship_type else None


class Group(Base, TimestampMixin):
    __tablename__ = "groups"
    __table_args__ = (
        UniqueConstraint("university_id", "name", "admission_year", name="uq_group_univ_name_year"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    course: Mapped[int] = mapped_column(Integer, nullable=False)
    admission_year: Mapped[int] = mapped_column(Integer, nullable=False)

    university_id: Mapped[int] = mapped_column(ForeignKey("universities.id", ondelete="RESTRICT"), nullable=False)

    curator_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    curator_photo: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # путь/URL

    university: Mapped["University"] = relationship(back_populates="groups")
    students: Mapped[List["Student"]] = relationship(
        back_populates="group", cascade="all, delete-orphan"
    )

    @property
    def university_name(self) -> str | None:
        return self.university.name if self.university else None


class Student(Base, TimestampMixin):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="RESTRICT"), nullable=False)

    group: Mapped["Group"] = relationship(back_populates="students")
    assignments: Mapped[List["ScholarshipAssignment"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )

    @property
    def group_name(self) -> str | None:
        return self.group.name if self.group else None


class ScholarshipAssignment(Base, TimestampMixin):
    __tablename__ = "scholarship_assignments"
    __table_args__ = (
        UniqueConstraint("student_id", "semester", name="uq_student_semester"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    semester: Mapped[int] = mapped_column(Integer, nullable=False)

    scholarship_type_id: Mapped[int] = mapped_column(ForeignKey("scholarship_types.id", ondelete="RESTRICT"), nullable=False)

    # "снимок" вычисленного размера на момент назначения
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    student: Mapped["Student"] = relationship(back_populates="assignments")
    scholarship_type: Mapped["ScholarshipType"] = relationship(back_populates="assignments")

    @property
    def student_full_name(self) -> str | None:
        return self.student.full_name if self.student else None

    @property
    def scholarship_type_name(self) -> str | None:
        return self.scholarship_type.name if self.scholarship_type else None

    @property
    def group_name(self) -> str | None:
        if not self.student or not self.student.group:
            return None
        return self.student.group.name
