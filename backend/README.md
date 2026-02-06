# MoneyMentor Backend - Investment Planning Engine

## Overview
FastAPI backend for inflation-aware investment planning using Mean-Variance Optimization (Markowitz Model).

## Architecture

### Data Flow
```
Market Data (Daily) → Returns Calculation → Statistics → Covariance Matrix
                                                ↓
User Request → Inflation Model → Portfolio Optimization → SIP/Lumpsum Calculation
```

### Key Components

1. **Data Fetcher** (`data_fetcher.py`)
   - Fetches NIFTY50, Gold, Bonds, Cash data
   - Calculates log returns
   - Stores in PostgreSQL

2. **Portfolio Optimizer** (`portfolio_optimizer.py`)
   - Mean-Variance Optimization using cvxpy
   - Risk-based constraints
   - Returns optimal asset allocation

3. **Scheduler** (`scheduler.py`)
   - Daily automated data updates (6 PM IST)
   - Runs on app startup

## Installation

### Prerequisites
- Python 3.9+
- PostgreSQL (or SQLite for development)

### Setup Steps

1. **Create virtual environment**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. **Initialize database**
```bash
python -c "from database import init_db; init_db()"
```

5. **Run the server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or simply:
```bash
python main.py
```

## API Endpoints

### 1. Recommend Portfolio
**POST** `/api/recommend-portfolio`

Generate investment recommendation based on user inputs.

**Request Body:**
```json
{
  "inflated_goal": 1850000,
  "years": 5,
  "risk_profile": "medium",
  "time_horizon": "medium",
  "investment_type": "sip",
  "user_id": "user123",
  "goal_type": "car",
  "current_price": 1000000
}
```

**Response:**
```json
{
  "inflated_goal": 1850000,
  "portfolio": {
    "Equity": 0.45,
    "Gold": 0.25,
    "Bonds": 0.20,
    "Cash": 0.10
  },
  "expected_return": 0.112,
  "portfolio_risk": 0.084,
  "monthly_sip": 21500,
  "total_invested": 1290000,
  "expected_wealth": 1850000,
  "optimization_status": "optimal",
  "message": "Invest ₹21,500 monthly via SIP to reach your goal"
}
```

### 2. Fetch Market Data
**POST** `/api/fetch-market-data`

Manually trigger market data fetch (usually automatic).

**Response:**
```json
{
  "status": "success",
  "message": "Market data fetch initiated",
  "results": {
    "nifty50": true,
    "gold": true,
    "bonds": true,
    "cash": true
  }
}
```

### 3. Get Asset Statistics
**GET** `/api/asset-statistics`

Get current expected returns and volatility.

**Response:**
```json
{
  "status": "success",
  "data": {
    "Equity": {
      "expected_annual_return": "12.45%",
      "annual_volatility": "18.23%"
    },
    "Gold": {
      "expected_annual_return": "8.12%",
      "annual_volatility": "12.45%"
    }
  }
}
```

## Portfolio Optimization Logic

### Mean-Variance Optimization

**Objective:**
Minimize portfolio risk (variance)

```
minimize: w^T Σ w
```

**Constraints:**
1. Weights sum to 1: `Σw = 1`
2. No short selling: `w ≥ 0`
3. Meet required return: `μ^T w ≥ R_required`
4. Risk-based equity bounds:
   - Low risk: 10-30% equity
   - Medium risk: 30-60% equity
   - High risk: 60-80% equity

### Return Calculation

**Expected Return:**
```
μ = mean(log_returns) × 252
```

**Volatility:**
```
σ = std(log_returns) × √252
```

**Covariance Matrix:**
```
Σ = cov(returns) × 252
```

### SIP Formula

```python
SIP = FV × r / ((1 + r)^n - 1)
```

Where:
- `FV` = Future value (inflated goal)
- `r` = Monthly return = Annual return / 12
- `n` = Months = Years × 12

### Lumpsum Formula

```python
PV = FV / (1 + r)^n
```

## Database Schema

### Tables

1. **asset_prices**
   - date, asset, price

2. **asset_returns**
   - date, asset, return_value

3. **asset_stats**
   - asset, expected_return, volatility, last_updated

4. **covariance_matrix**
   - date, matrix_json

5. **user_goals**
   - user_id, goal_type, inflated_price, risk_profile, recommended_portfolio, monthly_sip

## Automated Jobs

### Daily Data Update (6 PM IST)

1. Fetch NIFTY50, Gold, Bonds, Cash prices
2. Calculate log returns
3. Update asset statistics
4. Update covariance matrix

## Data Sources

| Asset | Source | Symbol |
|-------|--------|--------|
| Equity | Yahoo Finance | ^NSEI (NIFTY50) |
| Gold | Yahoo Finance | GOLDBEES.NS |
| Bonds | Synthetic/RBI | 10Y G-Sec |
| Cash | RBI | Repo Rate |

## Testing

### Test API locally
```bash
curl http://localhost:8000/api/health
```

### Test portfolio recommendation
```bash
curl -X POST http://localhost:8000/api/recommend-portfolio \
  -H "Content-Type: application/json" \
  -d '{
    "inflated_goal": 1850000,
    "years": 5,
    "risk_profile": "medium",
    "investment_type": "sip"
  }'
```

## Deployment

### Using Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `GOLD_API_KEY`: GoldAPI key (optional)
- `ENVIRONMENT`: development/production

## Troubleshooting

### Database Connection Issues
- Check DATABASE_URL in .env
- For development, use SQLite: `sqlite:///./moneymentor.db`

### Data Fetch Failures
- NIFTY50: Check internet connection and Yahoo Finance API
- Gold: Fallback to GOLDBEES.NS ETF
- Bonds: Uses synthetic data (replace with RBI API)

### Optimization Failures
- Falls back to rule-based allocation
- Check asset statistics are populated
- Verify covariance matrix exists

## Performance

- API response time: < 500ms
- Daily data update: ~2-3 minutes
- Database queries: Indexed for fast lookups

## Security

- CORS enabled (restrict in production)
- No authentication (add JWT/OAuth in production)
- Input validation via Pydantic
- SQL injection protection via SQLAlchemy ORM

## Next Steps

1. **Integrate Inflation Model**: Connect with your friend's inflation prediction API
2. **Add Authentication**: Implement user login/signup
3. **Historical Backtesting**: Add endpoint to backtest portfolio performance
4. **Notifications**: Email/SMS alerts for goal progress
5. **Dashboard Analytics**: Add portfolio performance tracking

## Contact & Support

For issues or questions, check the logs:
```bash
tail -f logs/app.log  # If logging configured
```

## License
MIT License - MoneyMentor Project
