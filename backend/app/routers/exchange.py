from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Coin, CoinImage, ExchangeListing, ExchangeOffer, Notification, MetalType, CoinCondition, CoinImage
from app.schemas.exchange import ExchangeListingCreate, ExchangeOfferCreate

router = APIRouter(prefix="/exchange", tags=["Exchange"])


@router.get("/listings")
async def get_exchange_listings(
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
    """Список монет, выставленных на обмен (другими пользователями)"""
    
    query = select(Coin).join(
        ExchangeListing, ExchangeListing.coin_id == Coin.id
    ).where(
        ExchangeListing.is_active == True,
        Coin.user_id != current_user.id
    )
    
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
    
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    response = []
    for coin in coins:
        owner_result = await db.execute(select(User).where(User.id == coin.user_id))
        owner = owner_result.scalar_one()
        
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
    
    return {
        "items": response,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/listings", status_code=status.HTTP_201_CREATED)
async def add_to_exchange(
    data: ExchangeListingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Выставить свою монету на обмен"""
    
    coin_result = await db.execute(
        select(Coin).where(Coin.id == data.coin_id, Coin.user_id == current_user.id)
    )
    coin = coin_result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(404, "Монета не найдена")
    
    existing = await db.execute(
        select(ExchangeListing).where(ExchangeListing.coin_id == data.coin_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Монета уже выставлена на обмен")
    
    listing = ExchangeListing(
        coin_id=data.coin_id,
        user_id=current_user.id,
        is_active=True
    )
    db.add(listing)
    await db.commit()
    
    return {"message": "Монета выставлена на обмен"}


@router.delete("/listings/{coin_id}")
async def remove_from_exchange(
    coin_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Снять монету с обмена"""
    
    result = await db.execute(
        select(ExchangeListing).where(
            ExchangeListing.coin_id == coin_id,
            ExchangeListing.user_id == current_user.id
        )
    )
    listing = result.scalar_one_or_none()
    
    if not listing:
        raise HTTPException(404, "Монета не найдена в списке обмена")
    
    await db.delete(listing)
    await db.commit()
    
    return {"message": "Монета снята с обмена"}


@router.post("/offers/batch", status_code=status.HTTP_201_CREATED)
async def create_batch_exchange_offer(
    data: ExchangeOfferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать групповое предложение обмена"""
    
    # Проверяем, что есть хотя бы одна монета
    if (not data.offered_coin_ids or len(data.offered_coin_ids) == 0) and (not data.requested_coin_ids or len(data.requested_coin_ids) == 0):
        raise HTTPException(400, "Выберите хотя бы одну монету для отправки или получения")
    
    target_user_id = None
    
    # Если есть запрашиваемые монеты, определяем получателя из них
    if data.requested_coin_ids and len(data.requested_coin_ids) > 0:
        requested_coins = []
        for coin_id in data.requested_coin_ids:
            result = await db.execute(select(Coin).where(Coin.id == coin_id))
            coin = result.scalar_one_or_none()
            if not coin:
                raise HTTPException(404, f"Монета {coin_id} не найдена")
            requested_coins.append(coin)
        
        target_user_id = requested_coins[0].user_id
        for coin in requested_coins:
            if coin.user_id != target_user_id:
                raise HTTPException(400, "Все запрашиваемые монеты должны принадлежать одному пользователю")
        
        if target_user_id == current_user.id:
            raise HTTPException(400, "Нельзя отправлять предложение на свои монеты")
    
    # Если нет запрашиваемых монет, но есть предлагаемые (подарок), используем to_user_id
    elif data.offered_coin_ids and len(data.offered_coin_ids) > 0 and data.to_user_id:
        target_user_id = data.to_user_id
        if target_user_id == current_user.id:
            raise HTTPException(400, "Нельзя отправлять подарок самому себе")
        
        # Проверяем, что предлагаемые монеты принадлежат текущему пользователю
        for coin_id in data.offered_coin_ids:
            result = await db.execute(select(Coin).where(Coin.id == coin_id, Coin.user_id == current_user.id))
            coin = result.scalar_one_or_none()
            if not coin:
                raise HTTPException(404, f"Ваша монета {coin_id} не найдена")
    
    else:
        raise HTTPException(400, "Не удалось определить получателя")
    
    # Убеждаемся, что offered_coin_ids и requested_coin_ids всегда массивы, не None
    offered_coin_ids = data.offered_coin_ids if data.offered_coin_ids else []
    requested_coin_ids = data.requested_coin_ids if data.requested_coin_ids else []
    
    # Создаём предложение
    offer = ExchangeOffer(
        offered_coin_ids=offered_coin_ids,
        requested_coin_ids=requested_coin_ids,
        from_user_id=current_user.id,
        to_user_id=target_user_id,
        status="pending",
        message=data.message
    )
    db.add(offer)
    await db.flush()
    
    from_user_name = current_user.username or current_user.email.split('@')[0]
    
    offered_count = len(offered_coin_ids)
    requested_count = len(requested_coin_ids)
    
    if offered_count == 0 and requested_count > 0:
        notification_content = f"Пользователь {from_user_name} хочет получить {requested_count} монет из вашей коллекции"
    elif offered_count > 0 and requested_count == 0:
        notification_content = f"Пользователь {from_user_name} дарит вам {offered_count} своих монет"
    else:
        notification_content = f"Пользователь {from_user_name} предлагает обмен: {offered_count} своих монет на {requested_count} ваших монет"
    
    notification = Notification(
        user_id=target_user_id,
        type="exchange_offer",
        content=notification_content,
        related_offer_id=offer.id
    )
    db.add(notification)
    
    await db.commit()
    
    return {"message": "Предложение отправлено", "offer_id": offer.id}

@router.get("/offers/sent")
async def get_sent_offers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отправленные предложения обмена"""
    
    result = await db.execute(
        select(ExchangeOffer).where(ExchangeOffer.from_user_id == current_user.id)
    )
    offers = result.scalars().all()
    
    response = []
    for offer in offers:
        # Получаем информацию о предлагаемых монетах с изображениями
        offered_coins = []
        if offer.offered_coin_ids:
            for coin_id in offer.offered_coin_ids:
                if coin_id:
                    coin_result = await db.execute(select(Coin).where(Coin.id == coin_id))
                    coin = coin_result.scalar_one_or_none()
                    if coin:
                        # Загружаем изображения для монеты
                        img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
                        images = img_result.scalars().all()
                        
                        offered_coins.append({
                            "id": coin.id,
                            "name": coin.name,
                            "year": coin.year,
                            "country": coin.country,
                            "denomination": coin.denomination,
                            "metal": coin.metal.value if hasattr(coin.metal, 'value') else coin.metal,
                            "condition": coin.condition.value if hasattr(coin.condition, 'value') else coin.condition,
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
        
        # Получаем информацию о запрашиваемых монетах с изображениями
        requested_coins = []
        if offer.requested_coin_ids:
            for coin_id in offer.requested_coin_ids:
                if coin_id:
                    coin_result = await db.execute(select(Coin).where(Coin.id == coin_id))
                    coin = coin_result.scalar_one_or_none()
                    if coin:
                        # Загружаем изображения для монеты
                        img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
                        images = img_result.scalars().all()
                        
                        requested_coins.append({
                            "id": coin.id,
                            "name": coin.name,
                            "year": coin.year,
                            "country": coin.country,
                            "denomination": coin.denomination,
                            "metal": coin.metal.value if hasattr(coin.metal, 'value') else coin.metal,
                            "condition": coin.condition.value if hasattr(coin.condition, 'value') else coin.condition,
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
        
        response.append({
            "id": offer.id,
            "offered_coin_ids": offer.offered_coin_ids or [],
            "requested_coin_ids": offer.requested_coin_ids or [],
            "offered_coins": offered_coins,
            "requested_coins": requested_coins,
            "from_user_id": offer.from_user_id,
            "to_user_id": offer.to_user_id,
            "status": offer.status,
            "message": offer.message,
            "created_at": offer.created_at,
            "updated_at": offer.updated_at
        })
    
    return response


@router.get("/offers/received")
async def get_received_offers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Входящие предложения обмена"""
    
    result = await db.execute(
        select(ExchangeOffer).where(ExchangeOffer.to_user_id == current_user.id)
    )
    offers = result.scalars().all()
    
    response = []
    for offer in offers:
        # Получаем информацию о предлагаемых монетах с изображениями
        offered_coins = []
        if offer.offered_coin_ids:
            for coin_id in offer.offered_coin_ids:
                if coin_id:
                    coin_result = await db.execute(select(Coin).where(Coin.id == coin_id))
                    coin = coin_result.scalar_one_or_none()
                    if coin:
                        # Загружаем изображения для монеты
                        img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
                        images = img_result.scalars().all()
                        
                        offered_coins.append({
                            "id": coin.id,
                            "name": coin.name,
                            "year": coin.year,
                            "country": coin.country,
                            "denomination": coin.denomination,
                            "metal": coin.metal.value if hasattr(coin.metal, 'value') else coin.metal,
                            "condition": coin.condition.value if hasattr(coin.condition, 'value') else coin.condition,
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
        
        # Получаем информацию о запрашиваемых монетах с изображениями
        requested_coins = []
        if offer.requested_coin_ids:
            for coin_id in offer.requested_coin_ids:
                if coin_id:
                    coin_result = await db.execute(select(Coin).where(Coin.id == coin_id))
                    coin = coin_result.scalar_one_or_none()
                    if coin:
                        # Загружаем изображения для монеты
                        img_result = await db.execute(select(CoinImage).where(CoinImage.coin_id == coin.id))
                        images = img_result.scalars().all()
                        
                        requested_coins.append({
                            "id": coin.id,
                            "name": coin.name,
                            "year": coin.year,
                            "country": coin.country,
                            "denomination": coin.denomination,
                            "metal": coin.metal.value if hasattr(coin.metal, 'value') else coin.metal,
                            "condition": coin.condition.value if hasattr(coin.condition, 'value') else coin.condition,
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
        
        response.append({
            "id": offer.id,
            "offered_coin_ids": offer.offered_coin_ids or [],
            "requested_coin_ids": offer.requested_coin_ids or [],
            "offered_coins": offered_coins,
            "requested_coins": requested_coins,
            "from_user_id": offer.from_user_id,
            "to_user_id": offer.to_user_id,
            "status": offer.status,
            "message": offer.message,
            "created_at": offer.created_at,
            "updated_at": offer.updated_at
        })
    
    return response

@router.put("/offers/{offer_id}/accept")
async def accept_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Принять предложение обмена (меняет владельцев монет)"""
    
    result = await db.execute(
        select(ExchangeOffer).where(
            ExchangeOffer.id == offer_id,
            ExchangeOffer.to_user_id == current_user.id,
            ExchangeOffer.status == "pending"
        )
    )
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(404, "Предложение не найдено или уже обработано")
    
    # Меняем владельцев предлагаемых монет (отправитель -> получатель)
    if offer.offered_coin_ids and len(offer.offered_coin_ids) > 0:
        for coin_id in offer.offered_coin_ids:
            coin_result = await db.execute(select(Coin).where(Coin.id == coin_id))
            coin = coin_result.scalar_one_or_none()
            if coin:
                coin.user_id = offer.to_user_id
        
        # Удаляем из списка обмена
        for coin_id in offer.offered_coin_ids:
            listing_result = await db.execute(
                select(ExchangeListing).where(ExchangeListing.coin_id == coin_id)
            )
            listing = listing_result.scalar_one_or_none()
            if listing:
                await db.delete(listing)
    
    # Меняем владельцев запрашиваемых монет (получатель -> отправитель)
    if offer.requested_coin_ids and len(offer.requested_coin_ids) > 0:
        for coin_id in offer.requested_coin_ids:
            coin_result = await db.execute(select(Coin).where(Coin.id == coin_id))
            coin = coin_result.scalar_one_or_none()
            if coin:
                coin.user_id = offer.from_user_id
        
        # Удаляем из списка обмена
        for coin_id in offer.requested_coin_ids:
            listing_result = await db.execute(
                select(ExchangeListing).where(ExchangeListing.coin_id == coin_id)
            )
            listing = listing_result.scalar_one_or_none()
            if listing:
                await db.delete(listing)
    
    offer.status = "accepted"
    
    current_user_name = current_user.username or current_user.email.split('@')[0]
    
    # Уведомление для отправителя
    notification = Notification(
        user_id=offer.from_user_id,
        type="offer_accepted",
        content=f"Пользователь {current_user_name} принял ваше предложение обмена! Монеты обменяны.",
        related_offer_id=offer.id
    )
    db.add(notification)
    
    await db.commit()
    
    return {"message": "Предложение принято, монеты обменяны"}


@router.put("/offers/{offer_id}/reject")
async def reject_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отклонить предложение обмена"""
    
    result = await db.execute(
        select(ExchangeOffer).where(
            ExchangeOffer.id == offer_id,
            ExchangeOffer.to_user_id == current_user.id,
            ExchangeOffer.status == "pending"
        )
    )
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(404, "Предложение не найдено или уже обработано")
    
    offer.status = "rejected"
    
    current_user_name = current_user.username or current_user.email.split('@')[0]
    
    # Уведомление для отправителя
    notification = Notification(
        user_id=offer.from_user_id,
        type="offer_rejected",
        content=f"Пользователь {current_user_name} отклонил ваше предложение обмена",
        related_offer_id=offer.id
    )
    db.add(notification)
    
    await db.commit()
    
    return {"message": "Предложение отклонено"}

@router.put("/offers/{offer_id}/cancel")
async def cancel_offer(
    offer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Отменить своё предложение (только для отправителя)"""
    
    result = await db.execute(
        select(ExchangeOffer).where(
            ExchangeOffer.id == offer_id,
            ExchangeOffer.from_user_id == current_user.id,
            ExchangeOffer.status == "pending"
        )
    )
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(404, "Предложение не найдено или уже обработано")
    
    offer.status = "cancelled"
    await db.commit()
    
    return {"message": "Предложение отменено"}