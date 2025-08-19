from pydantic import BaseModel
from typing import Optional

class ImageUploadResponse(BaseModel):
    success: bool
    image_url: Optional[str] = None
    image_path: Optional[str] = None
    error: Optional[str] = None
