from pydantic import BaseModel
from typing import Optional


class BaseResponse(BaseModel):
    """基础响应模型"""
    code: str
    msg: str


class ResponseWithData(BaseModel):
    """带数据的响应模型"""
    base: BaseResponse
    data: Optional[dict] = None
