from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TimestampReadMixin(BaseModel):
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ScholarshipTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    base_amount: Decimal = Field(gt=0)


class ScholarshipTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    base_amount: Decimal | None = Field(default=None, gt=0)


class ScholarshipTypeRead(TimestampReadMixin):
    id: int
    name: str
    base_amount: Decimal


class UniversityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class UniversityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)


class UniversityRead(TimestampReadMixin):
    id: int
    name: str


class UniversityCoeffCreate(BaseModel):
    university_id: int
    scholarship_type_id: int
    coeff: Decimal = Field(gt=0)


class UniversityCoeffUpdate(BaseModel):
    coeff: Decimal | None = Field(default=None, gt=0)


class UniversityCoeffRead(TimestampReadMixin):
    id: int
    university_id: int
    scholarship_type_id: int
    coeff: Decimal
    university_name: str | None = None
    scholarship_type_name: str | None = None


class GroupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    course: int = Field(ge=1, le=6)
    admission_year: int = Field(ge=1990, le=2100)
    university_id: int
    curator_full_name: str = Field(min_length=1, max_length=255)
    curator_photo: str | None = None  # URL/путь


class GroupUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    course: int | None = Field(default=None, ge=1, le=6)
    admission_year: int | None = Field(default=None, ge=1990, le=2100)
    university_id: int | None = None
    curator_full_name: str | None = Field(default=None, min_length=1, max_length=255)
    curator_photo: str | None = None


class GroupRead(TimestampReadMixin):
    id: int
    name: str
    course: int
    admission_year: int
    university_id: int
    curator_full_name: str
    curator_photo: str | None
    university_name: str | None = None


class StudentCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    group_id: int
    address: str = Field(min_length=1)


class StudentUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    group_id: int | None = None
    address: str | None = Field(default=None, min_length=1)


class StudentRead(TimestampReadMixin):
    id: int
    full_name: str
    group_id: int
    address: str
    group_name: str | None = None


class ScholarshipAssignmentCreate(BaseModel):
    student_id: int
    semester: int = Field(ge=1, le=20)
    scholarship_type_id: int


class ScholarshipAssignmentUpdate(BaseModel):
    semester: int | None = Field(default=None, ge=1, le=20)
    scholarship_type_id: int | None = None


class ScholarshipAssignmentRead(TimestampReadMixin):
    id: int
    student_id: int
    semester: int
    scholarship_type_id: int
    amount: Decimal
    student_full_name: str | None = None
    scholarship_type_name: str | None = None
    group_name: str | None = None


class UserRegister(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: str = Field(min_length=5, max_length=255)
    last_name: str = Field(min_length=1, max_length=100)
    first_name: str = Field(min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    password: str = Field(min_length=6, max_length=255)


class UserProfileUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=100)
    email: str | None = Field(default=None, min_length=5, max_length=255)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    middle_name: str | None = Field(default=None, max_length=100)
    default_page_size: int | None = Field(default=None, ge=5, le=100)
    auto_refresh_seconds: int | None = Field(default=None, ge=0, le=3600)
    default_language: str | None = Field(default=None, pattern="^(ru|en)$")


class PasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=255)
    new_password: str = Field(min_length=6, max_length=255)


class UserRead(TimestampReadMixin):
    id: int
    username: str
    email: str
    last_name: str
    first_name: str
    middle_name: str | None
    full_name: str
    is_active: bool
    default_page_size: int
    auto_refresh_seconds: int
    default_language: str


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    user: UserRead | None = None


class RefreshTokenPayload(BaseModel):
    refresh_token: str = Field(min_length=1)
