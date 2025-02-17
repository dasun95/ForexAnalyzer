import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from database import SessionLocal, engine
import models
from sqlalchemy import desc
from sqlalchemy.orm import Session
from contextlib import contextmanager

def init_db():
    models.Base.metadata.create_all(bind=engine)

@contextmanager
def get_db():
    """Database session context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_forex_pairs():
    """Returns a list of common forex pairs"""
    return [
        "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", 
        "USDCHF=X", "NZDUSD=X", "USDCAD=X"
    ]

def get_or_create_forex_pair(db: Session, symbol: str):
    """Get or create forex pair in database"""
    pair = db.query(models.ForexPair).filter(models.ForexPair.symbol == symbol).first()
    if not pair:
        pair = models.ForexPair(symbol=symbol)
        db.add(pair)
        db.commit()
        db.refresh(pair)
    return pair

def save_price_data(db: Session, pair_id: int, df: pd.DataFrame, timeframe: str):
    """Save price data to database"""
    try:
        for index, row in df.iterrows():
            # Convert timestamp to Python datetime
            timestamp = pd.to_datetime(index).to_pydatetime()

            price_data = models.PriceData(
                pair_id=pair_id,
                timestamp=timestamp,
                open=float(row['Open']),
                high=float(row['High']),
                low=float(row['Low']),
                close=float(row['Close']),
                volume=float(row['Volume']) if 'Volume' in row else 0.0,
                timeframe=timeframe
            )
            db.add(price_data)
        db.commit()
    except Exception as e:
        db.rollback()
        raise Exception(f"Error saving price data: {str(e)}")

def get_forex_data(symbol, interval, period):
    """
    Fetches forex data for the specified symbol and timeframe
    """
    try:
        with get_db() as db:
            pair = get_or_create_forex_pair(db, symbol)

            # Fetch new data from yfinance
            ticker = yf.Ticker(symbol)
            df = ticker.history(interval=interval, period=period)

            if df.empty:
                raise ValueError("No data received from yfinance")

            # Save new data to database
            save_price_data(db, pair.id, df, interval)

            return df
    except Exception as e:
        raise Exception(f"Error fetching data: {str(e)}")

def format_price(price):
    """Formats price with appropriate decimal places"""
    return f"{price:.4f}"

def save_user_preference(symbol: str):
    """Save user's selected forex pair preference"""
    try:
        with get_db() as db:
            pref = models.UserPreference(selected_pair=symbol)
            db.add(pref)
            db.commit()
    except Exception as e:
        pass  # Silently handle preference save errors

def get_last_user_preference():
    """Get user's last selected forex pair"""
    try:
        with get_db() as db:
            pref = (
                db.query(models.UserPreference)
                .order_by(desc(models.UserPreference.last_viewed))
                .first()
            )
            return pref.selected_pair if pref else None
    except Exception:
        return None