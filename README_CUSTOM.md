# MoneyMentor — Project README

Version: 1.0

Overview
--------
MoneyMentor is a full-stack application that helps Indian investors plan and achieve financial goals by forecasting future costs (inflation-aware) and recommending optimized portfolio allocations using mean-variance optimization (Markowitz). The backend is a Python FastAPI service providing financial models and optimization. The frontend is a React + TypeScript app (Vite) that provides the user interface.

Key Features
------------
- Inflation prediction models for future cost estimation
- Portfolio optimization using Mean-Variance Optimization
- SIP and Lumpsum calculators
- Automated market-data fetching and scheduled updates
- Simple demo authentication and example credentials

Architecture & Ports
--------------------
- Frontend: React + TypeScript + Vite (default dev port: 8080)
- Backend: FastAPI (default port: 8000)
- Database: SQLite (moneymentor.db) by default; compatible with PostgreSQL

Quick start (Windows)
---------------------
1. Start both services using the provided script (PowerShell):

   .\start-dev.ps1

2. Or run manually:

   Backend (PowerShell):
   cd backend
   pip install -r requirements.txt
   python main.py

   Frontend (PowerShell):
   npm install
   npm run dev

3. Access:
- Frontend UI: http://localhost:8080
- Backend API: http://localhost:8000
- API docs: http://localhost:8000/docs

Project layout (important files)
--------------------------------
Root files
- package.json — Frontend dependencies and scripts (Vite, React, Tailwind, shadcn/ui)
- index.html — Frontend HTML entry (title, meta tags)
- start-dev.ps1 — One-click startup script (Windows)
- moneymentor.db — Local SQLite DB snapshot (if present)

Frontend (src/)
- main.tsx — React entry; mounts App
- App.tsx — Main app layout and routes
- pages/ — Feature pages (Investment planner, Dashboard, auth pages)
- components/ — Reusable UI components
- hooks/, contexts/ — React hooks and context providers for app state
- lib/ — utilities, API client wrappers
- index.css / tailwind setup — Styling

Backend (backend/)
- main.py — FastAPI app, routes and startup
- database.py — Database models and initialization (SQLite / SQLAlchemy)
- data_fetcher.py — Market data fetching (yfinance or other sources)
- inflation_models.py — Inflation prediction logic and helper functions
- gold_nn_model.py — Gold prediction neural-network utilities (if used)
- portfolio_optimizer.py — Mean-Variance optimization logic (convex optimization)
- show_gold_calc.py — Scripts to demonstrate gold calculations
- scheduler.py — APScheduler-based scheduler for automated updates
- models/ — ORM models and domain objects
- requirements.txt — Python dependencies for backend

Important scripts & instructions
-------------------------------
- start-dev.ps1 — Starts both frontend and backend (Windows convenience)
- backend/main.py — If developing backend only, run `python main.py`
- npm run dev — Start frontend in development mode

How MoneyMentor works (flow)
----------------------------
1. User enters a financial goal: target amount, time horizon, risk profile, investment type (SIP/Lumpsum).
2. Backend predicts future cost via inflation models (inflation_models.py) and other data-driven models (gold_nn_model.py).
3. portfolio_optimizer.py computes an optimal asset allocation using historical returns and covariance; constraints ensure non-negative weights and risk bounds.
4. SIP / lumpsum calculation computes required periodic or one-time investment to reach the inflated target.
5. Results and visualizations are returned to the frontend for display.

API Endpoints (examples)
------------------------
- GET /api/health — health check
- POST /api/recommend-portfolio — Input: {inflated_goal, years, risk_profile, investment_type} → Output: allocation, expected return, required SIP/lumpsum
- Other endpoints: market-data sync, user demo login (check backend/main.py)

Database and persistence
------------------------
- A local SQLite file (moneymentor.db) is included for quick testing. Database models are defined in backend/database.py and models/.
- To re-initialize: run a small Python snippet or the provided DB init command (see backend README or database.py).

Testing and Demo
----------------
- Demo credentials (if available in the project): demo@moneymentor.com / demo123
- Backend API docs: open http://localhost:8000/docs for interactive testing
- Example curl command (from project README):

  curl -X POST http://localhost:8000/api/recommend-portfolio \
    -H "Content-Type: application/json" \
    -d '{"inflated_goal": 1850000, "years": 5, "risk_profile": "medium", "investment_type": "sip"}'

Notes about the attached PDF
----------------------------
An academic guidelines PDF ("Guidelines thesis dissertaion report- Ph.D,M.E,B.E") is included in Inflation Models/. This repository's README and documentation structure were framed using that guideline as a reference: it helped shape the project documentation sections (overview, architecture, methodology, and academic context). The PDF is a reference for writing thesis-style descriptions and doesn't change code behavior.

Contributing & Future work
--------------------------
Contributions welcome. Suggested enhancements:
- Add user authentication (JWT/OAuth) and user-specific goal persistence
- Portfolio performance backtesting and historical simulations
- Tax-aware optimization and Indian tax rules
- Expand datasets (direct RBI APIs, more asset classes)

Contact / Support
-----------------
Open issues or PRs in this repository. For developer help: check backend logs, API docs, and the Quickstart instructions.

----
File created: README_CUSTOM.md — let me know if you want this to replace the existing README.md or to be merged/shortened for a project landing page.
