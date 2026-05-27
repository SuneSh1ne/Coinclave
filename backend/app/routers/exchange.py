from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Coin, ExchangeListing, ExchangeOffer, Notification, OfferStatus, MetalType, CoinCondition
from app.schemas.exchange import ExchangeListingCreate, ExchangeListingResponse, ExchangeOfferCreate, ExchangeOfferResponse

router = APIRouter(prefix="/exchange", tags=["Exchange"])

# ========== Монеты на обмен ==========

@router.get("/listings")
async def get_exchange_listings(
    country: Optional[str] = Query(None),
    metal: Optional[MetalType] = Query(None),
    year_from: Optional[int] = Query(None),
    year_to: Optional[int] = Query(None),
    condition: Optional[CoinCondition] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Список монет, выставленных на обмен (другими пользователями) с пагинацией"""
    
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
    
    # Считаем общее количество
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0
    
    # Пагинация
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    coins = result.scalars().all()
    
    # Добавляем информацию о владельце
    response = []
    for coin in coins:
        owner_result = await db.execute(select(User).where(User.id == coin.user_id))
        owner = owner_result.scalar_one()
        
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
            "owner_email": owner.email
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
    
    # Проверяем, что монета принадлежит пользователю
    coin_result = await db.execute(
        select(Coin).where(Coin.id == data.coin_id, Coin.user_id == current_user.id)
    )
    coin = coin_result.scalar_one_or_none()
    
    if not coin:
        raise HTTPException(404, "Монета не найдена")
    
    # Проверяем, не выставлена ли уже
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

# ========== Предложения обмена ==========

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
    return offers

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
    return offers

@router.post("/offers", status_code=status.HTTP_201_CREATED)
async def create_exchange_offer(
    data: ExchangeOfferCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создать предложение обмена"""
    
    # Проверяем, что предлагаемая монета принадлежит текущему пользователю
    offered_result = await db.execute(
        select(Coin).where(Coin.id == data.offered_coin_id, Coin.user_id == current_user.id)
    )
    offered_coin = offered_result.scalar_one_or_none()
    
    if not offered_coin:
        raise HTTPException(404, "Предлагаемая монета не найдена")
    
    # Проверяем, что запрашиваемая монета существует и выставлена на обмен
    requested_result = await db.execute(
        select(Coin).where(Coin.id == data.requested_coin_id)
    )
    requested_coin = requested_result.scalar_one_or_none()
    
    if not requested_coin:
        raise HTTPException(404, "Запрашиваемая монета не найдена")
    
    # Проверяем, что монета на обмене
    listing_result = await db.execute(
        select(ExchangeListing).where(
            ExchangeListing.coin_id == data.requested_coin_id,
            ExchangeListing.is_active == True
        )
    )
    if not listing_result.scalar_one_or_none():
        raise HTTPException(400, "Эта монета больше не доступна для обмена")
    
    if requested_coin.user_id == current_user.id:
        raise HTTPException(400, "Нельзя обмениваться со своим монетами")
    
    # Создаём предложение
    offer = ExchangeOffer(
        offered_coin_id=data.offered_coin_id,
        requested_coin_id=data.requested_coin_id,
        from_user_id=current_user.id,
        to_user_id=requested_coin.user_id,
        status=OfferStatus.PENDING,
        message=data.message
    )
    db.add(offer)
    await db.flush()
    
    # Создаём уведомление для получателя
    notification = Notification(
        user_id=requested_coin.user_id,
        type="exchange_offer",
        content=f"Пользователь {current_user.email} хочет обменять монету '{offered_coin.name}' на вашу монету '{requested_coin.name}'",
        related_offer_id=offer.id
    )
    db.add(notification)
    
    await db.commit()
    
    return {"message": "Предложение отправлено", "offer_id": offer.id}

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
            ExchangeOffer.status == OfferStatus.PENDING
        )
    )
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(404, "Предложение не найдено или уже обработано")
    
    # Получаем монеты
    offered_result = await db.execute(select(Coin).where(Coin.id == offer.offered_coin_id))
    offered_coin = offered_result.scalar_one()
    
    requested_result = await db.execute(select(Coin).where(Coin.id == offer.requested_coin_id))
    requested_coin = requested_result.scalar_one()
    
    # Меняем владельцев
    offered_coin.user_id = offer.to_user_id
    requested_coin.user_id = offer.from_user_id
    
    # Удаляем из списка обмена обе монеты
    for coin_id in [offer.offered_coin_id, offer.requested_coin_id]:
        listing_result = await db.execute(
            select(ExchangeListing).where(ExchangeListing.coin_id == coin_id)
        )
        listing = listing_result.scalar_one_or_none()
        if listing:
            await db.delete(listing)
    
    # Обновляем статус предложения
    offer.status = OfferStatus.ACCEPTED
    
    # Уведомление для отправителя
    notification = Notification(
        user_id=offer.from_user_id,
        type="offer_accepted",
        content=f"Пользователь {current_user.email} принял ваше предложение обмена! Монеты обменяны.",
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
            ExchangeOffer.status == OfferStatus.PENDING
        )
    )
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(404, "Предложение не найдено или уже обработано")
    
    offer.status = OfferStatus.REJECTED
    
    # Уведомление для отправителя
    notification = Notification(
        user_id=offer.from_user_id,
        type="offer_rejected",
        content=f"Пользователь {current_user.email} отклонил ваше предложение обмена",
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
            ExchangeOffer.status == OfferStatus.PENDING
        )
    )
    offer = result.scalar_one_or_none()
    
    if not offer:
        raise HTTPException(404, "Предложение не найдено или уже обработано")
    
    offer.status = OfferStatus.CANCELLED
    await db.commit()
    
    return {"message": "Предложение отменено"}