from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class ForexPair(Base):
    __tablename__ = "forex_pairs"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    price_data = relationship("PriceData", back_populates="pair")

class PriceData(Base):
    __tablename__ = "price_data"
    
    id = Column(Integer, primary_key=True, index=True)
    pair_id = Column(Integer, ForeignKey("forex_pairs.id"))
    timestamp = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    timeframe = Column(String)  # '5m', '1h', '1d'
    
    pair = relationship("ForexPair", back_populates="price_data")

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    selected_pair = Column(String)
    last_viewed = Column(DateTime, default=datetime.utcnow)
