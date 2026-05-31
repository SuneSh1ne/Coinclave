from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from io import StringIO
import csv
import os
import uuid

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Coin, CoinImage, MetalType, CoinCondition
from app.schemas.coin import CoinCreate, CoinUpdate, CoinResponse, CoinFilterParams

router = APIRouter(prefix="/api/coins", tags=["Coins"])

# Настройка папки для загрузок
UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def ensure_upload_dir():
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

async def save_coin_image(file: UploadFile, user_id: int, coin_id: int, is_obverse: bool) -> str:
    """Сохраняет изображение монеты и возвращает путь"""
    
    ensure_upload_dir()
    
    # Проверяем расширение
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Неподдерживаемый формат. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Проверяем размер
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(400, f"Файл слишком большой. Максимум 5MB")
    
    # Генерируем уникальное имя
    unique_name = f"user_{user_id}/coin_{coin_id}/{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(UPLOAD_DIR, unique_name)
    
    # Создаём папку если нужно
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    
    # Сохраняем файл
    with open(full_path, "wb") as buffer:
        buffer.write(content)
    
    return unique_name

async def delete_coin_image(image_path: str) -> None:
    """Удаляет файл изображения"""
    full_path = os.path.join(UPLOAD_DIR, image_path)
    if os.path.exists(full_path):
        os.remove(full_path)

@router.get("/")
async def get_my_coins(
    country: Optional[str] = Query(None),
    metal: Optional[MetalType] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    condition: Optional[CoinCondition] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список монет текущего пользователя с фильтрацией и пагинацией"""
    
    query = select(Coin).where(Coin.user_id == current_user.id)
    
    if country:
        query = query.where(Coin.country == country)
    if metal:
        query = query.where(Coin.metal == metal)
    if year_from:
        query = query.where(Coin.year >= year_from)
    if year_to:
        query = query.where(Coin.year <= year_to)
    if condition:
        query = query.where(Coin.condition == condition)
    if search:
        query = query.where(Coin.name.ilike(f"%{search}%"))
    
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    query = query.order_by(Coin.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    response_items = []
    for coin in coins:
        img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
        images = img_result.scalars().all()
        
        response_items.append({
            "id": coin.id,
            "user_id": coin.user_id,
            "name": coin.name,
            "year": coin.year,
            "country": coin.country,
            "denomination": coin.denomination,
            "metal": coin.metal,
            "condition": coin.condition,
            "purchase_price": coin.purchase_price,
            "estimated_value": coin.estimated_value,
            "created_at": coin.created_at,
            "updated_at": coin.updated_at,
            "images": [
                {
                    "id": img.id,
                    "image_path": img.image_path,
                    "is_obverse": img.is_obverse,
                    "uploaded_at": img.uploaded_at
                }
                for img in images
            ]
        })
    
    return {
        "items": response_items,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_coin(
    name: str = Form(...),
    year: int = Form(...),
    country: str = Form(...),
    denomination: str = Form(...),
    metal: MetalType = Form(...),
    condition: CoinCondition = Form(...),
    purchase_price: Optional[float] = Form(None),
    estimated_value: float = Form(...),
    images: List[UploadFile] = File(default=[]),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать новую монету с загрузкой изображений"""
    
    new_coin = Coin(
        user_id=current_user.id,
        name=name,
        year=year,
        country=country,
        denomination=denomination,
        metal=metal,
        condition=condition,
        purchase_price=purchase_price,
        estimated_value=estimated_value
    )
    
    db.add(new_coin)
    await db.flush()
    
    saved_images = []
    for idx, img in enumerate(images[:4]):
        if img and img.filename:
            is_obverse = (idx == 0)
            path = await save_coin_image(img, current_user.id, new_coin.id, is_obverse)
            coin_img = CoinImage(coin_id=new_coin.id, image_path=path, is_obverse=is_obverse)
            db.add(coin_img)
            saved_images.append(coin_img)
    
    await db.commit()
    await db.refresh(new_coin)
    
    return {
        "id": new_coin.id,
        "user_id": new_coin.user_id,
        "name": new_coin.name,
        "year": new_coin.year,
        "country": new_coin.country,
        "denomination": new_coin.denomination,
        "metal": new_coin.metal,
        "condition": new_coin.condition,
        "purchase_price": new_coin.purchase_price,
        "estimated_value": new_coin.estimated_value,
        "created_at": new_coin.created_at,
        "updated_at": new_coin.updated_at,
        "images": [
            {
                "id": img.id,
                "image_path": img.image_path,
                "is_obverse": img.is_obverse,
                "uploaded_at": img.uploaded_at
            }
            for img in saved_images
        ]
    }


@router.get("/{coin_id}")
async def get_coin(
    coin_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить детальную информацию о монете"""
    
    result = await db.execute(select(Coin).where(Coin.id == coin_id, Coin.user_id == current_user.id))
    coin = result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(404, "Монета не найдена")
    
    img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
    images = img_result.scalars().all()
    
    return {
        "id": coin.id,
        "user_id": coin.user_id,
        "name": coin.name,
        "year": coin.year,
        "country": coin.country,
        "denomination": coin.denomination,
        "metal": coin.metal,
        "condition": coin.condition,
        "purchase_price": coin.purchase_price,
        "estimated_value": coin.estimated_value,
        "created_at": coin.created_at,
        "updated_at": coin.updated_at,
        "images": [
            {
                "id": img.id,
                "image_path": img.image_path,
                "is_obverse": img.is_obverse,
                "uploaded_at": img.uploaded_at
            }
            for img in images
        ]
    }


# Схема для обновления монеты (JSON)
class CoinUpdateSchema(BaseModel):
    name: Optional[str] = None
    year: Optional[int] = None
    country: Optional[str] = None
    denomination: Optional[str] = None
    metal: Optional[MetalType] = None
    condition: Optional[CoinCondition] = None
    purchase_price: Optional[float] = None
    estimated_value: Optional[float] = None

@router.put("/{coin_id}")
async def update_coin(
    coin_id: int,
    coin_data: CoinUpdateSchema,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновить информацию о монете"""
    
    result = await db.execute(select(Coin).where(Coin.id == coin_id, Coin.user_id == current_user.id))
    coin = result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(404, "Монета не найдена")
    
    # Обновляем только переданные поля
    update_data = coin_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(coin, field, value)
    
    await db.commit()
    await db.refresh(coin)
    
    # Загружаем изображения для ответа
    img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
    images = img_result.scalars().all()
    
    return {
        "id": coin.id,
        "user_id": coin.user_id,
        "name": coin.name,
        "year": coin.year,
        "country": coin.country,
        "denomination": coin.denomination,
        "metal": coin.metal.value if hasattr(coin.metal, 'value') else coin.metal,
        "condition": coin.condition.value if hasattr(coin.condition, 'value') else coin.condition,
        "purchase_price": coin.purchase_price,
        "estimated_value": coin.estimated_value,
        "created_at": coin.created_at,
        "updated_at": coin.updated_at,
        "images": [
            {
                "id": img.id,
                "image_path": img.image_path,
                "is_obverse": img.is_obverse,
                "uploaded_at": img.uploaded_at
            }
            for img in images
        ]
    }

@router.post("/{coin_id}/images")
async def add_coin_images(
    coin_id: int,
    images: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Добавить изображения к существующей монете"""
    
    result = await db.execute(select(Coin).where(Coin.id == coin_id, Coin.user_id == current_user.id))
    coin = result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(404, "Монета не найдена")
    
    # Проверяем количество уже существующих изображений
    img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin_id))
    existing_count = len(img_result.scalars().all())
    
    saved_images = []
    for idx, img in enumerate(images[:4]):
        if existing_count + idx >= 4:
            break
        if img and img.filename:
            is_obverse = (existing_count == 0 and idx == 0)
            path = await save_coin_image(img, current_user.id, coin_id, is_obverse)
            coin_img = CoinImage(coin_id=coin_id, image_path=path, is_obverse=is_obverse)
            db.add(coin_img)
            saved_images.append(coin_img)
    
    await db.commit()
    
    return {
        "message": f"Добавлено {len(saved_images)} изображений",
        "images": [
            {
                "id": img.id,
                "image_path": img.image_path,
                "is_obverse": img.is_obverse
            }
            for img in saved_images
        ]
    }


@router.delete("/{coin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coin(
    coin_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить монету и все её изображения"""
    
    result = await db.execute(select(Coin).where(Coin.id == coin_id, Coin.user_id == current_user.id))
    coin = result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(404, "Монета не найдена")
    
    img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
    images = img_result.scalars().all()
    
    for img in images:
        await delete_coin_image(img.image_path)
    
    await db.delete(coin)
    await db.commit()


@router.get("/stats/total-value")
async def get_total_value(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить суммарную стоимость коллекции"""
    
    result = await db.execute(
        select(func.sum(Coin.estimated_value)).where(Coin.user_id == current_user.id)
    )
    total = result.scalar() or 0
    
    return {"total_value": float(total)}


@router.get("/export/{format}")
async def export_collection(
    format: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Экспорт коллекции в JSON или CSV"""
    from fastapi.responses import Response
    import json
    
    result = await db.execute(select(Coin).where(Coin.user_id == current_user.id))
    coins = result.scalars().all()
    
    data = []
    for coin in coins:
        img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
        images = img_result.scalars().all()
        
        data.append({
            "id": coin.id,
            "name": coin.name,
            "year": coin.year,
            "country": coin.country,
            "denomination": coin.denomination,
            "metal": coin.metal.value,
            "condition": coin.condition.value,
            "purchase_price": coin.purchase_price,
            "estimated_value": coin.estimated_value,
            "images": [img.image_path for img in images]
        })
    
    if format == "json":
        content = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        return Response(
            content=content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=coinclave_collection.json"}
        )
    
    elif format == "csv":
        output = StringIO()
        output.write('\ufeff')
        
        if data:
            fieldnames = ['id', 'name', 'year', 'country', 'denomination', 'metal', 'condition', 'purchase_price', 'estimated_value']
            writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            for row in data:
                writer.writerow({
                    'id': row['id'],
                    'name': row['name'],
                    'year': row['year'],
                    'country': row['country'],
                    'denomination': row['denomination'],
                    'metal': row['metal'],
                    'condition': row['condition'],
                    'purchase_price': row['purchase_price'],
                    'estimated_value': row['estimated_value']
                })
        
        return Response(
            content=output.getvalue().encode('utf-8'),
            media_type="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=coinclave_collection.csv"}
        )
    
    else:
        raise HTTPException(400, "Неверный формат. Используйте json или csv")


@router.get("/filters/countries")
async def get_unique_countries(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получить список всех стран, которые есть в коллекции пользователя"""
    
    result = await db.execute(
        select(Coin.country).where(Coin.user_id == current_user.id).distinct()
    )
    countries = result.scalars().all()
    
    return {"countries": sorted(countries)}