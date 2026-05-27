from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from io import StringIO
import csv

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Coin, CoinImage, MetalType, CoinCondition
from app.schemas.coin import CoinCreate, CoinUpdate, CoinResponse, CoinFilterParams
from app.services.file_upload import save_coin_image, delete_coin_image

router = APIRouter(prefix="/api/coins", tags=["Coins"])

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
    
    # Фильтрация
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
    
    # Считаем общее количество
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Пагинация
    query = query.order_by(Coin.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    # Загружаем изображения для каждой монеты отдельно
    response_items = []
    for coin in coins:
        img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
        images = img_result.scalars().all()
        
        # Преобразуем монету в словарь с изображениями
        coin_dict = {
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
        response_items.append(coin_dict)
    
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
    
    # Создаём монету
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
    
    # Сохраняем изображения
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
    
    # Формируем ответ с изображениями
    result = {
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
    
    return result


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
    
    # Загружаем изображения
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


@router.put("/{coin_id}")
async def update_coin(
    coin_id: int,
    coin_data: CoinUpdate,
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
    
    # Загружаем изображения
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
    
    # Удаляем файлы изображений
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
        return Response(
            content=json.dumps(data, indent=2, default=str),
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=collection.json"}
        )
    
    elif format == "csv":
        output = StringIO()
        if data:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=collection.csv"}
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


# ========== Управление изображениями ==========

@router.delete("/images/{image_id}")
async def delete_coin_image_endpoint(
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удалить конкретное изображение монеты"""
    
    result = await db.execute(select(CoinImage).where(CoinImage.id == image_id))
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(404, "Изображение не найдено")
    
    # Проверяем, что монета принадлежит текущему пользователю
    coin_result = await db.execute(select(Coin).where(Coin.id == image.coin_id, Coin.user_id == current_user.id))
    coin = coin_result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(403, "Нет доступа к этому изображению")
    
    await delete_coin_image(image.image_path)
    await db.delete(image)
    await db.commit()
    
    return {"message": "Изображение удалено"}


@router.post("/{coin_id}/images")
async def add_coin_image(
    coin_id: int,
    image: UploadFile = File(...),
    is_obverse: bool = Form(True),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Добавить новое изображение к существующей монете"""
    
    result = await db.execute(select(Coin).where(Coin.id == coin_id, Coin.user_id == current_user.id))
    coin = result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(404, "Монета не найдена")
    
    path = await save_coin_image(image, current_user.id, coin_id, is_obverse)
    
    new_image = CoinImage(
        coin_id=coin_id,
        image_path=path,
        is_obverse=is_obverse
    )
    db.add(new_image)
    await db.commit()
    await db.refresh(new_image)
    
    return {
        "id": new_image.id,
        "image_path": new_image.image_path,
        "is_obverse": new_image.is_obverse,
        "uploaded_at": new_image.uploaded_at
    }