from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Coin, CoinImage

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/search")
async def search_users(
    query: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Поиск других пользователей по email"""
    
    result = await db.execute(
        select(User)
        .where(User.email.ilike(f"%{query}%"))
        .where(User.id != current_user.id)
        .limit(20)
    )
    users = result.scalars().all()
    
    response = []
    for user in users:
        count_result = await db.execute(
            select(func.count(Coin.id)).where(Coin.user_id == user.id)
        )
        coins_count = count_result.scalar() or 0
        
        sum_result = await db.execute(
            select(func.sum(Coin.estimated_value)).where(Coin.user_id == user.id)
        )
        total_value = float(sum_result.scalar() or 0)
        
        response.append({
            "id": user.id,
            "email": user.email,
            "coins_count": coins_count,
            "total_value": total_value
        })
    
    return response


@router.get("/{user_id}/collection")
async def get_user_collection(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Просмотр коллекции другого пользователя (только чтение)"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    
    coins_result = await db.execute(select(Coin).where(Coin.user_id == user_id))
    coins = coins_result.scalars().all()
    
    response_coins = []
    for coin in coins:
        img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
        images = img_result.scalars().all()
        
        response_coins.append({
            "id": coin.id,
            "name": coin.name,
            "year": coin.year,
            "country": coin.country,
            "denomination": coin.denomination,
            "metal": coin.metal,
            "condition": coin.condition,
            "estimated_value": coin.estimated_value,
            "images": [
                {
                    "id": img.id,
                    "image_path": img.image_path,
                    "is_obverse": img.is_obverse
                }
                for img in images
            ]
        })
    
    return {
        "user_id": user.id,
        "user_email": user.email,
        "coins": response_coins
    }


@router.get("/{user_id}/stats")
async def get_user_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Статистика коллекции пользователя"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(404, "Пользователь не найден")
    
    count_result = await db.execute(
        select(func.count(Coin.id)).where(Coin.user_id == user_id)
    )
    coins_count = count_result.scalar() or 0
    
    sum_result = await db.execute(
        select(func.sum(Coin.estimated_value)).where(Coin.user_id == user_id)
    )
    total_value = float(sum_result.scalar() or 0)
    
    return {
        "user_id": user_id,
        "email": user.email,
        "coins_count": coins_count,
        "total_value": total_value
    }