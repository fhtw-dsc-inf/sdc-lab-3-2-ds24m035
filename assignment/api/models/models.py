# models.py
from pydantic import BaseModel
from typing import Optional

class ImageRequest(BaseModel):
    """
    Schema for incoming image generation requests.
    """
    prompt: str  # user prompt text
    negative_prompt: Optional[str] = None
    # You can add more optional fields here if needed (size, style, etc.)

class LocalImageRequest(ImageRequest):
    """
    Schema for incoming local image generation requests.
    """
    model: Optional[str] = "v1-5-pruned-emaonly"  # default model
    steps: Optional[int] = 30
    cfg_scale: Optional[float] = 8.0
    width: Optional[int] = 256
    height: Optional[int] = 256
    sampler_name: Optional[str] = "Euler a"
    n_iter: Optional[int] = 1

class ImageStatusResponse(BaseModel):
    """
    Schema for reporting image generation status back to client.
    """
    image_id: str           # UUID we generate for each image
    status: str             # queued | started | finished | failed | processing
    url: Optional[str] = None  # Optional direct URL to the image (if finished)
