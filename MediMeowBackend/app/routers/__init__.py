from app.routers.user import router as user_router
from app.routers.doctor import router as doctor_router
from app.routers.questionnaire import router as questionnaire_router
from app.routers.department import router as department_router

__all__ = [
    "user_router",
    "doctor_router",
    "questionnaire_router",
    "department_router"
]
