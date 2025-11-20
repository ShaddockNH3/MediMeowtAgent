from app.schemas.base import BaseResponse, ResponseWithData
from app.schemas.user import (
    UserRegister, UserLogin, UserBind, UserInfo, UserLoginResponse
)
from app.schemas.doctor import (
    DoctorLogin, DoctorInfo, DoctorReport, QueueResponse, 
    AIResult, SummaryResponse, KeyInfo as DoctorKeyInfo
)
from app.schemas.questionnaire import (
    Question, SavedAnswer, QuestionnaireDetail, QuestionnaireSubmit,
    QuestionnaireSubmitResponse, FileUploadResponse, SubmissionStatus,
    KeyInfo as QuestionnaireKeyInfo
)
from app.schemas.department import (
    DepartmentCreate, DepartmentInfo, DepartmentList
)

__all__ = [
    "BaseResponse",
    "ResponseWithData",
    "UserRegister",
    "UserLogin",
    "UserBind",
    "UserInfo",
    "UserLoginResponse",
    "DoctorLogin",
    "DoctorInfo",
    "DoctorReport",
    "QueueResponse",
    "AIResult",
    "SummaryResponse",
    "Question",
    "SavedAnswer",
    "QuestionnaireDetail",
    "QuestionnaireSubmit",
    "QuestionnaireSubmitResponse",
    "FileUploadResponse",
    "SubmissionStatus",
    "DepartmentCreate",
    "DepartmentInfo",
    "DepartmentList",
]
