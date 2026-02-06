"""
Database models for MoneyMentor
"""
from sqlalchemy import Column, Integer, Float, String, Date, JSON, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class AssetPrice(Base):
    """Historical price data for assets"""
    __tablename__ = "asset_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    asset = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AssetReturn(Base):
    """Calculated returns for assets"""
    __tablename__ = "asset_returns"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    asset = Column(String, nullable=False, index=True)
    return_value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class AssetStats(Base):
    """Statistical metrics for assets"""
    __tablename__ = "asset_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    asset = Column(String, nullable=False, unique=True, index=True)
    expected_return = Column(Float, nullable=False)
    volatility = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)

class CovarianceMatrix(Base):
    """Covariance matrix for portfolio optimization"""
    __tablename__ = "covariance_matrix"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    matrix_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserGoal(Base):
    """User financial goals"""
    __tablename__ = "user_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    goal_type = Column(String, nullable=False)
    current_price = Column(Float, nullable=False)
    target_year = Column(Integer, nullable=False)
    inflated_price = Column(Float, nullable=False)
    risk_profile = Column(String, nullable=False)
    investment_type = Column(String, nullable=False)
    recommended_portfolio = Column(JSON)
    monthly_sip = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./moneymentor.db")

# Support SQLite for development
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
