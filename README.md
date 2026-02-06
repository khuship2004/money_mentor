# 💰 MoneyMentor - Inflation-Aware Investment Planner

> AI-powered investment planning for Indian investors using Mean-Variance Optimization

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue.svg)](https://www.typescriptlang.org/)

## 🎯 What is MoneyMentor?

MoneyMentor helps Indian investors plan for their financial goals by:
1. **Predicting future costs** using inflation models
2. **Optimizing portfolio allocation** using Nobel Prize-winning algorithms
3. **Calculating exact investment amounts** (SIP or lumpsum) needed

### Key Features

✅ **Inflation-Aware Planning** - Predicts future cost of your goals  
✅ **AI-Optimized Portfolios** - Uses Mean-Variance Optimization (Markowitz Model)  
✅ **Indian Market Data** - NIFTY50, Gold, Bonds, RBI rates  
✅ **Risk-Based Allocation** - Low/Medium/High risk profiles  
✅ **SIP & Lumpsum Support** - Both investment types  
✅ **Automated Data Updates** - Daily market data refresh  
✅ **Beautiful UI** - Modern, responsive design  

## 🚀 Quick Start

### Option 1: One-Click Start (Windows)

```powershell
# Run the start script
.\start-dev.ps1
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**Terminal 2 - Frontend:**
```bash
npm run dev
```

**Access the app:**
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Sample Login: demo@moneymentor.com / demo123

## 📚 Documentation

- **[Quick Start Guide](QUICKSTART.md)** - Get running in 5 minutes
- **[Complete Project Documentation](PROJECT_DOCUMENTATION.md)** - Full technical details
- **[Financial Distribution Explained](FINANCIAL_DISTRIBUTION_EXPLAINED.md)** - Step-by-step calculation logic
- **[Backend README](backend/README.md)** - API documentation

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │ (TypeScript + Vite + shadcn/ui)
│  Port 8080      │
└────────┬────────┘
         │ REST API
         ↓
┌────────────────┐
│ FastAPI Backend│ (Python + cvxpy + SQLAlchemy)
│ Port 8000      │
└────────┬───────┘
         │
         ├──→ PostgreSQL/SQLite (Data storage)
         ├──→ Yahoo Finance (NIFTY50, Gold)
         ├──→ RBI API (Bond yields)
         └──→ Scheduler (Daily updates)
```

## 📊 How It Works

### The Complete Flow

**1. User Input →** Goal details, risk profile, investment type  
**2. Inflation Calculation →** Predicts future cost  
**3. Portfolio Optimization →** Mean-Variance Optimization finds optimal allocation  
**4. SIP/Lumpsum Calculation →** Computes required investment amount  
**5. Results Display →** Shows portfolio breakdown and investment plan

### Example

```
Input: Buy a Car for ₹10,00,000 in 5 years (Medium Risk, SIP)

↓ Inflation Prediction (5% annually)
Inflated Price: ₹12,76,282

↓ Portfolio Optimization
Equity: 45% | Gold: 25% | Bonds: 20% | Cash: 10%
Expected Return: 11.2% | Risk: 8.4%

↓ SIP Calculation
Monthly SIP: ₹18,641
Total Investment: ₹11,18,460
Expected Wealth: ₹12,76,282
Expected Gains: ₹1,57,822
```

## 🧮 The Math Behind It

### Portfolio Optimization (Mean-Variance)

```
minimize: w^T Σ w  (minimize portfolio risk)

subject to:
  Σw_i = 1              (weights sum to 100%)
  w_i ≥ 0               (no short selling)
  μ^T w ≥ R_required    (meet required return)
  w_equity ∈ [min, max] (risk constraints)
```

### SIP Formula

```
SIP = FV × r / ((1 + r)^n - 1)

where:
  FV = Future value (inflated goal)
  r = Monthly return
  n = Number of months
```

**📖 See [FINANCIAL_DISTRIBUTION_EXPLAINED.md](FINANCIAL_DISTRIBUTION_EXPLAINED.md) for complete derivations**

## 🔧 Technology Stack

**Frontend:** React 18 + TypeScript + Vite + shadcn/ui + Tailwind CSS  
**Backend:** FastAPI + Python 3.9+ + cvxpy + SQLAlchemy  
**Data:** yfinance + pandas + numpy  
**Database:** PostgreSQL / SQLite  
**Scheduling:** APScheduler

## 📁 Project Structure

```
moneymentor-future-guide/
├── backend/                      # FastAPI backend
│   ├── main.py                  # API endpoints
│   ├── portfolio_optimizer.py   # Optimization logic
│   ├── data_fetcher.py          # Market data
│   └── database.py              # Models
├── src/                         # React frontend
│   ├── pages/
│   │   ├── InvestmentPlanner.tsx  # Main feature
│   │   └── Dashboard.tsx
│   └── components/
├── QUICKSTART.md                # 5-minute guide
├── PROJECT_DOCUMENTATION.md     # Complete docs
└── FINANCIAL_DISTRIBUTION_EXPLAINED.md  # Math explained
```

## 🧪 Testing

**Test Credentials:**
- Email: `demo@moneymentor.com`
- Password: `demo123`

**Test API:**
```bash
# Health check
curl http://localhost:8000/api/health

# Portfolio recommendation
curl -X POST http://localhost:8000/api/recommend-portfolio \
  -H "Content-Type: application/json" \
  -d '{"inflated_goal": 1850000, "years": 5, "risk_profile": "medium", "investment_type": "sip"}'
```

## 🎓 Academic Context

**This project demonstrates:**
- Quantitative Finance (Mean-Variance Optimization)
- Full-Stack Development (React + FastAPI)
- Data Engineering (Automated pipelines)
- Financial Technology (Real-world fintech app)

**Why Mean-Variance Optimization?**
- ✅ Nobel Prize winning (Harry Markowitz, 1990)
- ✅ Mathematically proven
- ✅ Explainable (regulatory compliant)
- ✅ Industry standard

## 🔮 Future Enhancements

- [ ] User authentication (JWT/OAuth)
- [ ] Portfolio performance tracking
- [ ] Historical backtesting
- [ ] Multiple goals support
- [ ] Tax optimization
- [ ] Email/SMS notifications

## 📞 Support

**Common Issues:**
- Port in use: See [QUICKSTART.md](QUICKSTART.md)
- Module not found: `pip install -r backend/requirements.txt`
- Database errors: `python -c "from database import init_db; init_db()"`

**Getting Help:**
1. Check documentation files
2. Review API docs at http://localhost:8000/docs
3. Check terminal logs

## 🙏 Acknowledgments

- Harry Markowitz - Mean-Variance Optimization theory
- Yahoo Finance - Market data API
- FastAPI & React - Modern frameworks
- shadcn/ui - Beautiful components

---

**Built with ❤️ for Indian investors**

*Invest Smart. Plan Ahead. Achieve Goals.*
- Edit files directly within the Codespace and commit and push your changes once you're done.

## What technologies are used for this project?

This project is built with:

- Vite
- TypeScript
- React
- shadcn-ui
- Tailwind CSS

## How can I deploy this project?

Simply open [Lovable](https://lovable.dev/projects/36c018aa-b3ab-4876-bf7f-bc92a595f9b1) and click on Share -> Publish.

## Can I connect a custom domain to my Lovable project?

Yes, you can!

To connect a domain, navigate to Project > Settings > Domains and click Connect Domain.

Read more here: [Setting up a custom domain](https://docs.lovable.dev/features/custom-domain#custom-domain)
