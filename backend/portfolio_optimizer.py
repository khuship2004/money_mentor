"""
Portfolio allocation engine using Markowitz Mean-Variance Optimization.

This version implements the Nobel Prize-winning Mean-Variance Optimization
algorithm by Harry Markowitz. It uses scipy.optimize to solve the constrained
optimization problem and find the efficient frontier allocation.

Windows-compatible version: Uses scipy instead of cvxpy for better Windows support.
"""
from typing import Dict
import numpy as np
from scipy.optimize import minimize
import math

# Risk profile constraints
RISK_CONSTRAINTS = {
    "low": {"equity": (0.1, 0.3)},
    "medium": {"equity": (0.3, 0.6)},
    "high": {"equity": (0.6, 0.8)}
}

# Time horizon constraints
HORIZON_ADJUSTMENTS = {
    "short": {"equity_penalty": -0.1},  # Reduce equity for short term
    "medium": {"equity_penalty": 0.0},   # No adjustment
    "long": {"equity_penalty": 0.1}      # Increase equity for long term
}

# Historical asset statistics (annualized returns and volatilities)
ASSET_STATISTICS = {
    "Equity": {"return": 0.12, "volatility": 0.18},
    "Gold": {"return": 0.08, "volatility": 0.12},
    "Bonds": {"return": 0.065, "volatility": 0.05},
    "Cash": {"return": 0.055, "volatility": 0.01}
}

class PortfolioOptimizer:
    """Markowitz Mean-Variance Optimizer using cvxpy."""

    def __init__(self, db=None):
        self.db = db
        self.assets = ["Equity", "Gold", "Bonds", "Cash"]
        self.covariance_matrix = self._build_covariance_matrix()

    def _build_covariance_matrix(self) -> np.ndarray:
        """
        Build covariance matrix from historical correlations.
        
        Correlation matrix (empirical from Indian markets):
        - Equity-Gold: 0.30 (moderate negative correlation)
        - Equity-Bonds: -0.15 (negative, diversification)
        - Equity-Cash: -0.05 (low correlation)
        - Gold-Bonds: 0.10 (low positive)
        - Gold-Cash: 0.05 (very low)
        - Bonds-Cash: 0.20 (low positive)
        """
        # Volatilities (annual)
        volatilities = np.array([0.18, 0.12, 0.05, 0.01])
        
        # Correlation matrix
        correlation = np.array([
            [1.00,  0.30, -0.15, -0.05],  # Equity
            [0.30,  1.00,  0.10,  0.05],  # Gold
            [-0.15, 0.10,  1.00,  0.20],  # Bonds
            [-0.05, 0.05,  0.20,  1.00]   # Cash
        ])
        
        # Convert correlation to covariance: Cov = D @ Corr @ D
        # where D is diagonal matrix of volatilities
        D = np.diag(volatilities)
        covariance = D @ correlation @ D
        
        return covariance

    def optimize_portfolio(
        self,
        required_return: float,
        risk_profile: str,
        time_horizon: str = "medium",
    ) -> Dict:
        """
        Optimize portfolio using Markowitz Mean-Variance Optimization.
        
        Solves:
            minimize: w^T Σ w  (minimize risk)
            subject to:
                Σw_i = 1       (fully invested)
                w_i ≥ 0        (no short selling)
                μ^T w ≥ R_req  (meet required return)
                w_eq ∈ [min, max] (risk profile constraint)
        
        Uses scipy.optimize.minimize for Windows compatibility.
        """
        try:
            # Expected returns vector
            mu = np.array([
                ASSET_STATISTICS["Equity"]["return"],
                ASSET_STATISTICS["Gold"]["return"],
                ASSET_STATISTICS["Bonds"]["return"],
                ASSET_STATISTICS["Cash"]["return"]
            ])
            
            # Objective function: minimize portfolio variance
            def objective(w):
                return np.sqrt(w @ self.covariance_matrix @ w)  # Portfolio std dev
            
            # Constraint 1: weights sum to 1
            def constraint_sum_to_one(w):
                return np.sum(w) - 1
            
            # Constraint 2: meet required return
            def constraint_return(w):
                return np.dot(mu, w) - required_return
            
            # Get risk profile constraints
            equity_min, equity_max = RISK_CONSTRAINTS[risk_profile]["equity"]
            
            # Time horizon adjustments
            horizon_penalty = HORIZON_ADJUSTMENTS[time_horizon]["equity_penalty"]
            equity_min = max(0.05, equity_min + horizon_penalty)
            equity_max = min(0.85, equity_max + horizon_penalty)
            
            # Bounds for each weight: [0, 1]
            bounds = [(0, 1), (0, 1), (0, 1), (0, 1)]
            
            # Equity constraint bounds (stricter than general bounds)
            bounds[0] = (equity_min, equity_max)
            
            # Constraints
            constraints = [
                {"type": "eq", "fun": constraint_sum_to_one},
                {"type": "ineq", "fun": constraint_return}
            ]
            
            # Initial guess: equal weights
            w0 = np.array([0.25, 0.25, 0.25, 0.25])
            
            # Optimize using SLSQP method (good for non-linear constrained optimization)
            result = minimize(
                objective,
                w0,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
                options={"maxiter": 1000, "ftol": 1e-9}
            )
            
            if result.success:
                optimal_weights = result.x
                
                # Calculate metrics
                expected_return = float(mu @ optimal_weights)
                portfolio_variance = float(optimal_weights @ self.covariance_matrix @ optimal_weights)
                portfolio_risk = float(np.sqrt(portfolio_variance))
                
                # Build portfolio dict
                portfolio = {
                    self.assets[i]: float(optimal_weights[i])
                    for i in range(4)
                }
                
                # Normalize in case of numerical errors
                total_weight = sum(portfolio.values())
                if abs(total_weight - 1.0) > 0.01:  # If significantly off
                    portfolio = {k: v / total_weight for k, v in portfolio.items()}
                
                return {
                    "portfolio": portfolio,
                    "expected_return": expected_return,
                    "portfolio_risk": portfolio_risk,
                    "optimization_status": "optimal",
                    "solver_status": "success"
                }
            else:
                # Fallback to rule-based if optimization fails
                return self._rule_based_allocation(risk_profile, time_horizon, required_return)
                
        except Exception as e:
            print(f"Optimization error: {e}. Falling back to rule-based allocation.")
            return self._rule_based_allocation(risk_profile, time_horizon, required_return)
    
    def _rule_based_allocation(self, risk_profile: str, time_horizon: str, required_return: float) -> Dict:
        """Deterministic allocation with simple risk tweaks."""

        base_allocations = {
            "low": {"Equity": 0.20, "Gold": 0.15, "Bonds": 0.50, "Cash": 0.15},
            "medium": {"Equity": 0.45, "Gold": 0.25, "Bonds": 0.20, "Cash": 0.10},
            "high": {"Equity": 0.70, "Gold": 0.15, "Bonds": 0.10, "Cash": 0.05},
        }

        portfolio = dict(base_allocations.get(risk_profile, base_allocations["medium"]))

        # Adjust equity a bit for horizon
        if time_horizon == "short":
            portfolio["Equity"] = max(0.05, portfolio["Equity"] - 0.05)
            portfolio["Bonds"] = min(0.8, portfolio["Bonds"] + 0.03)
            portfolio["Cash"] = min(0.2, portfolio["Cash"] + 0.02)
        elif time_horizon == "long":
            portfolio["Equity"] = min(0.85, portfolio["Equity"] + 0.05)
            portfolio["Bonds"] = max(0.05, portfolio["Bonds"] - 0.03)

        # Normalize to ensure sum to 1
        total = sum(portfolio.values())
        if total != 0:
            portfolio = {k: round(v / total, 3) for k, v in portfolio.items()}

        # Expected returns (conservative estimates)
        return_estimates = {
            "Equity": 0.10,
            "Gold": 0.08,
            "Bonds": 0.065,
            "Cash": 0.055,
        }

        expected_return = sum(portfolio[a] * return_estimates[a] for a in portfolio)
        # Simple risk heuristic
        portfolio_risk = 0.14 if risk_profile == "high" else 0.09 if risk_profile == "medium" else 0.05

        return {
            "portfolio": portfolio,
            "expected_return": round(expected_return, 4),
            "portfolio_risk": round(portfolio_risk, 4),
            "optimization_status": "rule_based",
        }
    
def calculate_sip(future_value: float, annual_return: float, years: int) -> float:
    """
    Calculate monthly SIP amount required
    
    Formula: SIP = FV * r / ((1 + r)^n - 1)
    where r = monthly return, n = number of months
    """
    try:
        r = annual_return / 12
        n = years * 12
        
        if r == 0:
            return future_value / n
        
        sip = future_value * r / ((1 + r)**n - 1)
        return round(sip, 2)
    except Exception as e:
        print(f"Error calculating SIP: {e}")
        return 0.0


def calculate_lumpsum(future_value: float, annual_return: float, years: int) -> float:
    """
    Calculate lumpsum amount required
    
    Formula: PV = FV / (1 + r)^n
    """
    try:
        pv = future_value / ((1 + annual_return) ** years)
        return round(pv, 2)
    except Exception as e:
        print(f"Error calculating lumpsum: {e}")
        return 0.0
