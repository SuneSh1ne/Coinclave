from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, ARRAY, Enum
from sqlalchemy.orm import relationship
import enum

from app.database import Base


# Перечисления (добавляем обратно)
class MetalType(str, enum.Enum):
    GOLD = "gold"
    SILVER = "silver"
    COPPER = "copper"
    NICKEL = "nickel"
    BRASS = "brass"
    BRONZE = "bronze"
    ALUMINUM = "aluminum"
    BIMETALLIC = "bimetallic"


class CoinCondition(str, enum.Enum):
    POOR = "poor"
    FAIR = "fair"
    GOOD = "good"
    VERY_GOOD = "very_good"
    FINE = "fine"
    VERY_FINE = "very_fine"
    EXTREMELY_FINE = "extremely_fine"
    UNCIRCULATED = "uncirculated"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    theme = Column(String(20), default="light")
    
    # Relationships
    coins = relationship("Coin", back_populates="owner", cascade="all, delete-orphan")
    sent_offers = relationship("ExchangeOffer", foreign_keys="ExchangeOffer.from_user_id", back_populates="from_user")
    received_offers = relationship("ExchangeOffer", foreign_keys="ExchangeOffer.to_user_id", back_populates="to_user")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Coin(Base):
    __tablename__ = "coins"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    year = Column(Integer, nullable=False)
    country = Column(String(100), nullable=False)
    denomination = Column(String(100), nullable=False)
    metal = Column(Enum(MetalType), nullable=False)
    condition = Column(Enum(CoinCondition), nullable=False)
    purchase_price = Column(Float, nullable=True)
    estimated_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship("User", back_populates="coins")
    images = relationship("CoinImage", back_populates="coin", cascade="all, delete-orphan")
    exchange_listing = relationship("ExchangeListing", back_populates="coin", uselist=False, cascade="all, delete-orphan")


class CoinImage(Base):
    __tablename__ = "coin_images"
    
    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(Integer, ForeignKey("coins.id"), nullable=False)
    image_path = Column(String(500), nullable=False)
    is_obverse = Column(Boolean, default=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    coin = relationship("Coin", back_populates="images")


class ExchangeListing(Base):
    __tablename__ = "exchange_listings"
    
    id = Column(Integer, primary_key=True, index=True)
    coin_id = Column(Integer, ForeignKey("coins.id"), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    coin = relationship("Coin", back_populates="exchange_listing")


class ExchangeOffer(Base):
    __tablename__ = "exchange_offers"
    
    id = Column(Integer, primary_key=True, index=True)
    offered_coin_ids = Column(ARRAY(Integer), nullable=True)
    requested_coin_ids = Column(ARRAY(Integer), nullable=False)
    from_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending")
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="sent_offers")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="received_offers")


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String(50), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    related_offer_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="notifications")