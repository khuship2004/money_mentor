"""
FastAPI Main Application
MoneyMentor - Investment Planning API
"""
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Optional, Dict
from datetime import datetime

from database import init_db, get_db, UserGoal
from data_fetcher import DataFetcher, calculate_returns
from portfolio_optimizer import PortfolioOptimizer, calculate_sip, calculate_lumpsum
from scheduler import DataScheduler

# Initialize FastAPI app
app = FastAPI(
    title="MoneyMentor API",
    description="Inflation-aware investment planning for Indian investors",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class InflationInput(BaseModel):
    """Input from inflation prediction model"""
    goal_type: str = Field(..., description="Type of goal (car, house, education, etc.)")
    current_price: float = Field(..., gt=0, description="Current cost of goal in INR")
    target_year: int = Field(..., gt=2024, description="Target year")
    inflated_price: float = Field(..., gt=0, description="Predicted inflated cost")
    years: int = Field(..., gt=0, description="Investment horizon in years")

class InvestmentRequest(BaseModel):
    """User investment planning request"""
    inflated_goal: float = Field(..., gt=0, description="Target amount in INR")
    years: int = Field(..., gt=0, le=50, description="Investment horizon (1-50 years)")
    risk_profile: str = Field(..., description="Risk appetite: low, medium, high")
    time_horizon: str = Field(default="medium", description="Time horizon: short, medium, long")
    investment_type: str = Field(..., description="Investment type: sip or lumpsum")
    user_id: Optional[str] = Field(default="anonymous", description="User identifier")
    goal_type: Optional[str] = Field(default="custom", description="Goal type")
    current_price: Optional[float] = Field(default=None, description="Current price")

class PortfolioResponse(BaseModel):
    """Investment recommendation response"""
    inflated_goal: float
    portfolio: Dict[str, float]
    expected_return: float
    portfolio_risk: float
    monthly_sip: Optional[float] = None
    lumpsum_amount: Optional[float] = None
    investment_type: str
    total_invested: Optional[float] = None
    expected_wealth: Optional[float] = None
    optimization_status: str
    message: str

class DataFetchResponse(BaseModel):
    """Response for data fetch operation"""
    status: str
    message: str
    results: Dict

# Initialize database and stub scheduler on startup
scheduler = DataScheduler()

@app.on_event("startup")
async def startup_event():
    """Initialize database and start stub scheduler"""
    init_db()
    print("✓ Database initialized")

    scheduler.start()
    print("✓ Scheduler started (stub)")

@app.get("/")
async def root():
    """API health check"""
    return {
        "message": "MoneyMentor API is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.post("/api/recommend-portfolio", response_model=PortfolioResponse)
async def recommend_portfolio(
    request: InvestmentRequest,
    db: Session = Depends(get_db)
):
    """
    Main endpoint: Generate investment recommendation
    
    Takes inflated goal amount, risk profile, and horizon
    Returns optimized portfolio allocation and required investment
    """
    try:
        # Validate risk profile
        if request.risk_profile not in ["low", "medium", "high"]:
            raise HTTPException(status_code=400, detail="Risk profile must be low, medium, or high")
        
        # Validate investment type
        if request.investment_type not in ["sip", "lumpsum"]:
            raise HTTPException(status_code=400, detail="Investment type must be sip or lumpsum")
        
        # Validate time horizon
        if request.time_horizon not in ["short", "medium", "long"]:
            request.time_horizon = "medium"
        
        # Calculate required return
        # R_required = (FV/PV)^(1/T) - 1
        # For SIP, we'll use an iterative approach or approximate
        # For simplicity, assume we need to beat inflation by 4-6%
        min_required_return = 0.08  # Minimum 8% to beat inflation
        
        # Initialize portfolio optimizer
        optimizer = PortfolioOptimizer(db)
        
        # Optimize portfolio
        result = optimizer.optimize_portfolio(
            required_return=min_required_return,
            risk_profile=request.risk_profile,
            time_horizon=request.time_horizon
        )
        
        # Calculate investment amount
        portfolio_return = result["expected_return"]
        
        if request.investment_type == "sip":
            monthly_sip = calculate_sip(
                future_value=request.inflated_goal,
                annual_return=portfolio_return,
                years=request.years
            )
            total_invested = monthly_sip * request.years * 12
            
            response_data = {
                "inflated_goal": request.inflated_goal,
                "portfolio": result["portfolio"],
                "expected_return": result["expected_return"],
                "portfolio_risk": result["portfolio_risk"],
                "monthly_sip": monthly_sip,
                "lumpsum_amount": None,
                "investment_type": "sip",
                "total_invested": total_invested,
                "expected_wealth": request.inflated_goal,
                "optimization_status": result["optimization_status"],
                "message": f"Invest ₹{monthly_sip:,.0f} monthly via SIP to reach your goal"
            }
        else:
            lumpsum = calculate_lumpsum(
                future_value=request.inflated_goal,
                annual_return=portfolio_return,
                years=request.years
            )
            
            response_data = {
                "inflated_goal": request.inflated_goal,
                "portfolio": result["portfolio"],
                "expected_return": result["expected_return"],
                "portfolio_risk": result["portfolio_risk"],
                "monthly_sip": None,
                "lumpsum_amount": lumpsum,
                "investment_type": "lumpsum",
                "total_invested": lumpsum,
                "expected_wealth": request.inflated_goal,
                "optimization_status": result["optimization_status"],
                "message": f"Invest ₹{lumpsum:,.0f} as lumpsum to reach your goal"
            }
        
        # Store in database
        goal_entry = UserGoal(
            user_id=request.user_id,
            goal_type=request.goal_type,
            current_price=request.current_price or 0,
            target_year=datetime.now().year + request.years,
            inflated_price=request.inflated_goal,
            risk_profile=request.risk_profile,
            investment_type=request.investment_type,
            recommended_portfolio=result["portfolio"],
            monthly_sip=monthly_sip if request.investment_type == "sip" else None
        )
        db.add(goal_entry)
        db.commit()
        
        return PortfolioResponse(**response_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")

@app.post("/api/fetch-market-data", response_model=DataFetchResponse)
async def fetch_market_data(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Manually trigger market data fetch
    Usually runs automatically via scheduler
    """
    try:
        fetcher = DataFetcher(db)
        results = fetcher.fetch_all()
        
        # Calculate returns in background
        background_tasks.add_task(calculate_returns, db)
        
        return DataFetchResponse(
            status="success",
            message="Market data fetch initiated",
            results=results
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@app.get("/api/asset-statistics")
async def get_asset_statistics(db: Session = Depends(get_db)):
    """Get current asset statistics (returns and volatility)"""
    try:
        optimizer = PortfolioOptimizer(db)
        stats = optimizer.calculate_asset_statistics()
        
        # Convert to readable format
        readable_stats = {}
        for asset, values in stats.items():
            asset_name = optimizer.asset_map.get(asset, asset)
            readable_stats[asset_name] = {
                "expected_annual_return": f"{values['expected_return']*100:.2f}%",
                "annual_volatility": f"{values['volatility']*100:.2f}%"
            }
        
        return {
            "status": "success",
            "data": readable_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

@app.get("/api/health")
async def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check"""
    try:
        # Check database
        db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
