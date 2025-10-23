# photos/processor.py
import io
from typing import Optional
from PIL import Image
from utils.logger import logger

def validate_image_bytes(image_bytes: bytes) -> bool:
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        return True
    except Exception as e:
        return False
    
def is_valid_image_file(filename: Optional[str], mime_type: Optional[str]) -> bool:
    valid_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp', '.tiff', '.tif'}
    
    valid_mime_types = {
        'image/jpeg', 'image/jpg', 'image/png', 
        'image/gif', 'image/bmp', 'image/webp',
        'image/tiff', 'image/x-icon'
    }
    
    if mime_type:
        mime_lower = mime_type.lower()
        if mime_lower in valid_mime_types:
            logger.debug(f"Valid image MIME type: {mime_type}")
            return True
    
    if filename:
        filename_lower = filename.lower()
        for ext in valid_extensions:
            if filename_lower.endswith(ext):
                logger.debug(f"Valid image extension: {filename}")
                return True
    
    logger.debug(f"Not a valid image file. Filename: {filename}, MIME: {mime_type}")
    return False