import os
import tempfile
import aiofiles
from typing import Optional

from utils import logger

async def download_temp_file(bot, file_path: str, user_id: int) -> tuple[str, str]:
    temp_dir = tempfile.mkdtemp(prefix=f"user_{user_id}_")
    temp_path = os.path.join(temp_dir, "temp.jpg")
    
    await bot.download_file(file_path, destination=temp_path)
    
    return temp_path, temp_dir

async def save_temp_bytes(content: bytes, prefix: str) -> str:
    fd, path = tempfile.mkstemp(prefix=prefix, suffix='.jpg')
    with os.fdopen(fd, 'wb') as f:
        f.write(content)
    return path

def cleanup_file(path: Optional[str]):
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError as e:
            pass

def cleanup_temp_dir(temp_dir: Optional[str]):
    if temp_dir and os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)