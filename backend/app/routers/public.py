from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import Optional, List

from app.database import get_db
from app.models import Coin, CoinImage, User, MetalType, CoinCondition

router = APIRouter(prefix="/public", tags=["Public"])

@router.get("/feed")
async def get_public_feed(
    country: Optional[str] = Query(None),
    metal: Optional[MetalType] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    condition: Optional[CoinCondition] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Публичная лента монет из разных коллекций с фильтрацией"""
    
    query = select(Coin)
    
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
    
    query = query.order_by(desc(Coin.created_at)).offset(offset).limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    response = []
    for coin in coins:
        # Получаем владельца
        owner_result = await db.execute(select(User).where(User.id == coin.user_id))
        owner = owner_result.scalar_one()
        
        # Получаем изображения
        img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
        images = img_result.scalars().all()
        
        response.append({
            "id": coin.id,
            "name": coin.name,
            "year": coin.year,
            "country": coin.country,
            "denomination": coin.denomination,
            "metal": coin.metal.value,
            "condition": coin.condition.value,
            "estimated_value": coin.estimated_value,
            "owner_id": owner.id,
            "owner_name": owner.username or owner.email.split('@')[0],
            "images": [
                {
                    "id": img.id,
                    "image_path": img.image_path,
                    "is_obverse": img.is_obverse
                }
                for img in images
            ]
        })
    
    return response


@router.get("/filters")
async def get_public_filters(
    db: AsyncSession = Depends(get_db)
):
    """Получить доступные значения для фильтров"""
    
    # Все страны из всех монет
    countries_result = await db.execute(select(Coin.country).distinct())
    countries = [c for c in countries_result.scalars().all() if c]
    
    # Все металлы
    metals = [m.value for m in MetalType]
    
    # Все состояния
    conditions = [c.value for c in CoinCondition]
    
    return {
        "countries": sorted(countries),
        "metals": metals,
        "conditions": conditions
    }

@router.get("/filters/countries")
async def get_all_countries(
    db: AsyncSession = Depends(get_db)
):
    """Получить список всех стран из всех монет на сайте"""
    
    result = await db.execute(select(Coin.country).distinct())
    countries = [c for c in result.scalars().all() if c]
    
    return {"countries": sorted(countries)}

@router.get("/stats")
async def get_public_stats(db: AsyncSession = Depends(get_db)):
    """Статистика для главной страницы"""
    
    # Общее количество монет
    coins_result = await db.execute(select(func.count(Coin.id)))
    total_coins = coins_result.scalar() or 0
    
    # Количество пользователей
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0
    
    # Количество стран
    countries_result = await db.execute(select(Coin.country).distinct())
    countries = [c for c in countries_result.scalars().all() if c]
    total_countries = len(countries)
    
    return {
        "total_coins": total_coins,
        "total_users": total_users,
        "total_countries": total_countries
    }
    