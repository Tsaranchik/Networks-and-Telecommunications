from decimal import Decimal
from pydantic import BaseModel, Field


class ScholarshipTypeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    base_amount: Decimal = Field(gt=0)


class ScholarshipTypeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    base_amount: Decimal | None = Field(default=None, gt=0)


class ScholarshipTypeRead(BaseModel):
    id: int
    name: str
    base_amount: Decimal

    class Config:
        from_attributes = True


class UniversityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)


class UniversityUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)


class UniversityRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class UniversityCoeffCreate(BaseModel):
    university_id: int
    scholarship_type_id: int
    coeff: Decimal = Field(gt=0)


class UniversityCoeffUpdate(BaseModel):
    coeff: Decimal | None = Field(default=None, gt=0)


class UniversityCoeffRead(BaseModel):
    id: int
    university_id: int
    scholarship_type_id: int
    coeff: Decimal

    class Config:
        from_attributes = True


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


class GroupRead(BaseModel):
    id: int
    name: str
    course: int
    admission_year: int
    university_id: int
    curator_full_name: str
    curator_photo: str | None

    class Config:
        from_attributes = True


class StudentCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    group_id: int
    address: str = Field(min_length=1)


class StudentUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    group_id: int | None = None
    address: str | None = Field(default=None, min_length=1)


class StudentRead(BaseModel):
    id: int
    full_name: str
    group_id: int
    address: str

    class Config:
        from_attributes = True


class ScholarshipAssignmentCreate(BaseModel):
    student_id: int
    semester: int = Field(ge=1, le=20)
    scholarship_type_id: int


class ScholarshipAssignmentUpdate(BaseModel):
    semester: int | None = Field(default=None, ge=1, le=20)
    scholarship_type_id: int | None = None


class ScholarshipAssignmentRead(BaseModel):
    id: int
    student_id: int
    semester: int
    scholarship_type_id: int
    amount: Decimal

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


