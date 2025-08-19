from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from ..core.deps import get_current_active_user
from ..models.user import User
from ..schemas.upload import ImageUploadResponse
import os
import uuid
from PIL import Image
import io

router = APIRouter()

@router.post("/image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user)
):
    """上传图片文件"""
    try:
        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="只支持图片文件")
        
        # 验证文件大小（10MB）
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="文件大小不能超过10MB")
        
        # 读取文件内容
        content = await file.read()
        
        # 验证图片格式
        try:
            image = Image.open(io.BytesIO(content))
            image.verify()
        except Exception:
            raise HTTPException(status_code=400, detail="无效的图片文件")
        
        # 生成唯一文件名
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        filename = f"{uuid.uuid4()}{file_extension}"
        
        # 确保上传目录存在
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存文件
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 返回文件URL - 使用完整URL
        image_url = f"http://localhost:8000/uploads/{filename}"
        
        return ImageUploadResponse(
            success=True,
            image_url=image_url,
            image_path=file_path
        )
        
    except HTTPException:
        raise
    except Exception as e:
        return ImageUploadResponse(
            success=False,
            error=f"上传失败: {str(e)}"
        )

@router.post("/image-url")
async def process_image_url(
    image_url: str,
    current_user: User = Depends(get_current_active_user)
):
    """处理图片URL"""
    try:
        # TODO: 实现图片URL验证和下载
        # 这里可以添加图片URL的有效性检查
        
        return {
            "success": True,
            "image_url": image_url,
            "message": "图片URL处理成功"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"处理失败: {str(e)}"
        }
