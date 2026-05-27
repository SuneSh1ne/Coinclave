import os
import shutil
from pathlib import Path
from typing import List
from fastapi import UploadFile, HTTPException
import uuid

from app.config import settings

UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = settings.max_file_size_mb * 1024 * 1024

async def save_coin_image(file: UploadFile, user_id: int, coin_id: int, is_obverse: bool) -> str:
    """Сохраняет изображение монеты и возвращает путь"""
    
    # Проверяем расширение
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Неподдерживаемый формат. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Проверяем размер
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"Файл слишком большой. Максимум {settings.max_file_size_mb}MB")
    
    # Генерируем уникальное имя
    unique_name = f"user_{user_id}/coin_{coin_id}/{ 'obverse' if is_obverse else 'reverse' }_{uuid.uuid4().hex}{ext}"
    full_path = UPLOAD_DIR / unique_name
    
    # Создаём папку если нужно
    full_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Сохраняем файл
    with open(full_path, "wb") as buffer:
        buffer.write(content)
    
    return str(unique_name)

async def delete_coin_image(image_path: str) -> None:
    """Удаляет файл изображения"""
    full_path = UPLOAD_DIR / image_path
    if full_path.exists():
        full_path.unlink()