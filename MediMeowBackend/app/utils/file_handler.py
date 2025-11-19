import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from config import settings


async def save_upload_file(file: UploadFile) -> tuple[str, str, int]:
    """
    保存上传的文件
    
    返回: (file_id, file_path, file_size)
    """
    # 验证文件大小
    file.file.seek(0, 2)  # 移动到文件末尾
    file_size = file.file.tell()  # 获取文件大小
    file.file.seek(0)  # 移回文件开头
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件大小超过限制 ({settings.MAX_FILE_SIZE} bytes)"
        )
    
    # 创建上传目录
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成唯一文件ID和文件名
    file_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    filename = f"{file_id}{file_extension}"
    file_path = upload_dir / filename
    
    # 异步保存文件
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return file_id, str(file_path), file_size


def delete_file(file_path: str) -> bool:
    """删除文件"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_path(file_id: str) -> str:
    """根据文件ID获取文件路径"""
    upload_dir = Path(settings.UPLOAD_DIR)
    # 查找匹配的文件
    for file_path in upload_dir.glob(f"{file_id}.*"):
        return str(file_path)
    raise HTTPException(status_code=404, detail="文件不存在")
