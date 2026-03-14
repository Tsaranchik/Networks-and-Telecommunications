from fastapi import APIRouter

from app.api.routers.scholarship_types import router as scholarship_types_router
from app.api.routers.universities import router as universities_router
from app.api.routers.university_coeffs import router as university_coeffs_router
from app.api.routers.groups import router as groups_router
from app.api.routers.students import router as students_router
from app.api.routers.assignments import router as assignments_router
from app.api.routers.media import router as media_router

api_router = APIRouter()

api_router.include_router(scholarship_types_router)
api_router.include_router(universities_router)
api_router.include_router(university_coeffs_router)
api_router.include_router(groups_router)
api_router.include_router(students_router)
api_router.include_router(assignments_router)
api_router.include_router(media_router)
