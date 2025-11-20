from typing import Optional, Any
from app.schemas.base import BaseResponse, ResponseWithData


def success_response(
    msg: str = "success",
    data: Optional[Any] = None
) -> dict:
    """成功响应"""
    response = {
        "base": {
            "code": "10000",
            "msg": msg
        }
    }
    if data is not None:
        response["data"] = data
    return response


def error_response(
    code: str = "10001",
    msg: str = "error"
) -> dict:
    """错误响应"""
    return {
        "base": {
            "code": code,
            "msg": msg
        }
    }
