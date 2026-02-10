"""
Inflation Models Integration Module
Provides inflation rates for Gold, Real Estate, Car, and Children Education
Uses multiple calculation methods for accuracy:
1. CAGR (Compound Annual Growth Rate)
2. Geometric Mean of YoY Returns
3. Linear Regression on Log Prices
4. Weighted Recent Average
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from scipy import stats
import os

# Excel file path - relative to backend folder
EXCEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "Inflation Models",
    "combined_dataset_20251005_175959.xlsx"
)


class InflationRatesProvider:
    """
    Provides inflation rates calculated using CAGR methodology
    from the inflation models
    """
    
    def __init__(self, excel_path: Optional[str] = None):
        self.excel_path = excel_path or EXCEL_PATH
        self._cached_rates: Dict = {}
        self._load_rates()
    
    def _load_rates(self):
        """Load and calculate inflation rates from data sources"""
        try:
            self._cached_rates = {
                'gold': self._calculate_gold_inflation(),
                'real_estate': self._calculate_real_estate_inflation(),
                'car': self._calculate_car_inflation(),
                'education': self._calculate_education_inflation(),
            }
        except Exception as e:
            print(f"Warning: Could not load from Excel, using default rates: {e}")
            # Fallback to pre-calculated historical averages
            self._cached_rates = self._get_default_rates()
    
    def _get_default_rates(self) -> Dict:
        """Default inflation rates based on historical analysis"""
        return {
            'gold': {
                'cagr': 14.03,
                'total_inflation': 383.19,
                'avg_yoy': 14.50,
                'period': '2014-2026',
                'years': 12,
                'data_source': 'Historical Average',
                'description': 'Gold price inflation based on historical trends'
            },
            'real_estate': {
                'cagr': 7.26,
                'total_inflation': 187.0,
                'avg_yoy': 7.50,
                'period': '2010-2025',
                'years': 15,
                'data_source': 'RBI/NHB HPI',
                'description': 'Housing Price Index based inflation',
                'city_wise': {
                    'Hyderabad': 9.72,
                    'Bangalore': 8.87,
                    'Mumbai': 7.88,
                    'Pune': 7.88,
                    'Delhi': 7.83,
                    'Chennai': 7.11,
                    'Ahmedabad': 7.11,
                    'Kolkata': 6.18
                }
            },
            'car': {
                'cagr': 5.50,
                'total_inflation': 85.0,
                'avg_yoy': 5.80,
                'period': '2010-2024',
                'years': 14,
                'data_source': 'Historical Average',
                'description': 'Vehicle and consumer goods price inflation'
            },
            'education': {
                'cagr': 11.50,
                'total_inflation': 700.0,
                'avg_yoy': 12.00,
                'period': '2005-2025',
                'years': 20,
                'data_source': 'Education Surveys',
                'description': 'Children education cost inflation',
                'categories': {
                    'school': {
                        'budget': 10.97,
                        'mid_range': 13.24,
                        'premium': 17.48,
                        'average': 13.90
                    },
                    'higher_education': {
                        'govt_college': 12.25,
                        'private_college': 17.81,
                        'engineering': 19.17,
                        'medical': 24.12,
                        'mba': 22.16,
                        'average': 19.10
                    },
                    'coaching': {
                        'school_tuition': 16.54,
                        'iit_jee': 22.48,
                        'neet': 22.48,
                        'upsc': 21.93,
                        'average': 20.86
                    }
                }
            }
        }
    
    def _calculate_cagr(self, start_value: float, end_value: float, years: int) -> float:
        """Calculate Compound Annual Growth Rate"""
        if start_value > 0 and years > 0:
            return ((end_value / start_value) ** (1 / years) - 1) * 100
        return 0.0
    
    def _calculate_geometric_mean(self, yearly_prices: pd.Series) -> float:
        """
        Calculate Geometric Mean of Year-over-Year growth rates
        Uses ALL consecutive year pairs, not just first and last
        """
        # Calculate growth rate for each consecutive year
        growth_rates = yearly_prices / yearly_prices.shift(1)
        growth_rates = growth_rates.dropna()
        
        if len(growth_rates) == 0:
            return 0.0
        
        # Geometric mean = (r1 × r2 × r3 × ... × rn)^(1/n) - 1
        geometric_mean = (np.prod(growth_rates) ** (1 / len(growth_rates)) - 1) * 100
        return geometric_mean
    
    def _calculate_regression_rate(self, years: np.ndarray, prices: np.ndarray) -> Dict:
        """
        Calculate inflation rate using Linear Regression on log-transformed prices
        This uses ALL data points and fits an exponential growth curve
        
        Log(Price) = a + b*Year  →  Price = e^a × e^(b×Year)
        Annual growth rate = e^b - 1
        """
        # Log-transform prices for exponential regression
        log_prices = np.log(prices)
        
        # Linear regression on log prices
        slope, intercept, r_value, p_value, std_err = stats.linregress(years, log_prices)
        
        # Convert slope back to annual growth rate
        # If log(P) = a + b*t, then P = e^(a+bt), so annual multiplier = e^b
        annual_rate = (np.exp(slope) - 1) * 100
        
        return {
            'rate': annual_rate,
            'r_squared': r_value ** 2,  # How well the model fits (0-1)
            'slope': slope,
            'intercept': intercept
        }
    
    def _calculate_weighted_average(self, yearly_data: pd.DataFrame, price_col: str) -> float:
        """
        Calculate weighted average giving more importance to recent years
        Recent data is more relevant for future predictions
        
        Weights: Most recent year = n, second most recent = n-1, ..., oldest = 1
        """
        n = len(yearly_data)
        if n < 2:
            return 0.0
        
        # Calculate YoY changes
        yoy_changes = yearly_data[price_col].pct_change().dropna() * 100
        
        # Create weights (1, 2, 3, ..., n) - higher weight for recent years
        weights = np.arange(1, len(yoy_changes) + 1)
        
        # Weighted average
        weighted_avg = np.average(yoy_changes, weights=weights)
        return weighted_avg
    
    def _calculate_all_methods(self, yearly_data: pd.DataFrame, price_col: str = 'Avg_Price') -> Dict:
        """
        Calculate inflation using ALL methods and return comprehensive results
        """
        years = yearly_data['Year'].values
        prices = yearly_data[price_col].values
        
        first_year = int(years[0])
        last_year = int(years[-1])
        first_price = float(prices[0])
        last_price = float(prices[-1])
        total_years = last_year - first_year
        
        # Method 1: CAGR (uses first and last only)
        cagr = self._calculate_cagr(first_price, last_price, total_years)
        
        # Method 2: Geometric Mean (uses ALL consecutive year pairs)
        geometric_mean = self._calculate_geometric_mean(yearly_data[price_col])
        
        # Method 3: Regression (uses ALL data points)
        regression = self._calculate_regression_rate(years.astype(float), prices.astype(float))
        
        # Method 4: Weighted Average (uses ALL years, weights recent higher)
        weighted_avg = self._calculate_weighted_average(yearly_data, price_col)
        
        # Method 5: Simple Average YoY
        yoy_changes = yearly_data[price_col].pct_change().dropna() * 100
        simple_avg_yoy = float(yoy_changes.mean())
        
        # Best Estimate: Weighted combination of methods
        # Regression is most accurate when R² is high, otherwise use geometric mean
        if regression['r_squared'] > 0.85:
            best_estimate = regression['rate'] * 0.4 + geometric_mean * 0.3 + weighted_avg * 0.3
        else:
            best_estimate = geometric_mean * 0.4 + weighted_avg * 0.35 + cagr * 0.25
        
        return {
            'cagr': round(cagr, 2),
            'geometric_mean': round(geometric_mean, 2),
            'regression_rate': round(regression['rate'], 2),
            'regression_r_squared': round(regression['r_squared'], 4),
            'weighted_average': round(weighted_avg, 2),
            'simple_avg_yoy': round(simple_avg_yoy, 2),
            'best_estimate': round(best_estimate, 2),
            'total_inflation': round(((last_price - first_price) / first_price) * 100, 2),
            'period': f'{first_year}-{last_year}',
            'years': total_years,
            'start_price': round(first_price, 2),
            'end_price': round(last_price, 2),
            'data_points_used': len(yearly_data)
        }

    def _calculate_gold_inflation(self) -> Dict:
        """Calculate gold inflation from Excel data using ALL data points"""
        try:
            gold_data = pd.read_excel(self.excel_path, sheet_name='Gold_Data')
            gold_data['Date'] = pd.to_datetime(gold_data['Date'])
            gold_data['Year'] = gold_data['Date'].dt.year
            
            # Aggregate to yearly averages
            yearly = gold_data.groupby('Year')['Price'].agg(['mean']).reset_index()
            yearly.columns = ['Year', 'Avg_Price']
            
            # Use comprehensive calculation with ALL methods
            results = self._calculate_all_methods(yearly, 'Avg_Price')
            
            # Add metadata
            results['data_source'] = 'Excel Dataset (All Methods)'
            results['description'] = 'Gold price inflation using multiple calculation methods'
            results['method_used'] = 'best_estimate'  # Weighted combination of all methods
            
            return results
            
        except Exception as e:
            print(f"Error calculating gold inflation: {e}")
            return self._get_default_rates()['gold']
    
    def _calculate_real_estate_inflation(self) -> Dict:
        """Calculate real estate inflation using RBI/NHB HPI data with ALL methods"""
        # Using embedded HPI data (same as in real_estate_inflation.py)
        hpi_data = {
            'Year': [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'HPI_Index': [100, 111, 126, 143, 158, 167, 175, 183, 191, 198, 195, 203, 218, 237, 261, 287]
        }
        
        df = pd.DataFrame(hpi_data)
        df.columns = ['Year', 'Avg_Price']  # Rename for consistency with _calculate_all_methods
        
        # Use comprehensive calculation with ALL methods
        results = self._calculate_all_methods(df, 'Avg_Price')
        
        # Add city-wise data
        city_cagr = {
            'Hyderabad': 9.72,
            'Bangalore': 8.87,
            'Mumbai': 7.88,
            'Pune': 7.88,
            'Delhi': 7.83,
            'Chennai': 7.11,
            'Ahmedabad': 7.11,
            'Kolkata': 6.18
        }
        
        results['data_source'] = 'RBI/NHB HPI (All Methods)'
        results['description'] = 'Housing Price Index inflation using multiple calculation methods'
        results['method_used'] = 'best_estimate'
        results['city_wise'] = city_cagr
        
        return results
    
    def _calculate_car_inflation(self) -> Dict:
        """Calculate car price inflation from Excel data using ALL methods"""
        try:
            car_data = pd.read_excel(self.excel_path, sheet_name='Car Data')
            
            # Aggregate to yearly averages
            yearly = car_data.groupby('year')['selling_price'].agg(['mean']).reset_index()
            yearly.columns = ['Year', 'Avg_Price']
            
            # Use comprehensive calculation with ALL methods
            results = self._calculate_all_methods(yearly, 'Avg_Price')
            
            # Add metadata
            results['data_source'] = 'Excel Dataset (All Methods)'
            results['description'] = 'Vehicle price inflation using multiple calculation methods'
            results['method_used'] = 'best_estimate'
            
            return results
        except Exception as e:
            print(f"Error calculating car inflation: {e}")
            return self._get_default_rates()['car']
    
    def _calculate_education_inflation(self) -> Dict:
        """
        Calculate education inflation for children's education planning.
        Uses realistic data and CAGR for each category.
        
        Focus: What parents typically spend on children's education
        - School fees (primary expense for most families)
        - College/University (UG programs)
        - Coaching/Tuition
        """
        # School Education Data (Annual Fees - what parents pay yearly)
        school_data = {
            'Year': [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014,
                     2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'Budget_School': [15000, 16500, 18000, 20000, 22000, 25000, 28000, 32000, 36000, 40000,
                              45000, 50000, 55000, 62000, 70000, 72000, 75000, 82000, 92000, 105000, 120000],
            'Mid_Range_School': [35000, 40000, 45000, 52000, 60000, 70000, 82000, 95000, 110000, 125000,
                                  145000, 165000, 185000, 210000, 240000, 250000, 265000, 295000, 330000, 375000, 425000],
            'Premium_School': [80000, 95000, 115000, 140000, 170000, 200000, 240000, 290000, 350000, 420000,
                               500000, 600000, 720000, 850000, 1000000, 1050000, 1150000, 1300000, 1500000, 1750000, 2000000]
        }
        
        df = pd.DataFrame(school_data)
        years = len(df) - 1  # 20 years
        
        # Calculate CAGR for school categories (most reliable for long-term data)
        budget_cagr = self._calculate_cagr(df['Budget_School'].iloc[0], df['Budget_School'].iloc[-1], years)
        mid_cagr = self._calculate_cagr(df['Mid_Range_School'].iloc[0], df['Mid_Range_School'].iloc[-1], years)
        premium_cagr = self._calculate_cagr(df['Premium_School'].iloc[0], df['Premium_School'].iloc[-1], years)
        
        # Also calculate geometric mean for school data (uses all years)
        df_budget = df[['Year', 'Budget_School']].copy()
        df_budget.columns = ['Year', 'Avg_Price']
        budget_geo = self._calculate_geometric_mean(df_budget['Avg_Price'])
        
        df_mid = df[['Year', 'Mid_Range_School']].copy()
        df_mid.columns = ['Year', 'Avg_Price']
        mid_geo = self._calculate_geometric_mean(df_mid['Avg_Price'])
        
        df_premium = df[['Year', 'Premium_School']].copy()
        df_premium.columns = ['Year', 'Avg_Price']
        premium_geo = self._calculate_geometric_mean(df_premium['Avg_Price'])
        
        # Average of CAGR and Geometric Mean for each school type
        budget_rate = (budget_cagr + budget_geo) / 2
        mid_rate = (mid_cagr + mid_geo) / 2
        premium_rate = (premium_cagr + premium_geo) / 2
        
        # School average - weighted by what most families choose
        # 50% mid-range, 35% budget, 15% premium
        school_avg = budget_rate * 0.35 + mid_rate * 0.50 + premium_rate * 0.15
        
        # Higher Education - Using industry-standard estimates
        # Based on AISHE reports and fee trends
        higher_ed_rates = {
            'govt_college': 8.0,       # Government colleges increase slower
            'private_college': 12.0,    # Private colleges
            'engineering': 10.5,        # Engineering (avg of govt & private)
            'medical': 15.0,            # Medical education (high but realistic)
            'mba': 11.5                 # MBA programs
        }
        # Weighted average - most students go to regular colleges, not medical/mba
        higher_ed_avg = (
            higher_ed_rates['govt_college'] * 0.25 +
            higher_ed_rates['private_college'] * 0.30 +
            higher_ed_rates['engineering'] * 0.25 +
            higher_ed_rates['medical'] * 0.10 +
            higher_ed_rates['mba'] * 0.10
        )
        
        # Coaching/Tuition Data
        coaching_rates = {
            'school_tuition': 10.0,     # Regular home tuition
            'iit_jee': 15.0,            # IIT-JEE coaching (premium)
            'neet': 14.0,               # NEET coaching
            'upsc': 12.0                # UPSC coaching
        }
        # Most students do regular tuition, fewer do competitive exam coaching
        coaching_avg = (
            coaching_rates['school_tuition'] * 0.60 +
            coaching_rates['iit_jee'] * 0.15 +
            coaching_rates['neet'] * 0.15 +
            coaching_rates['upsc'] * 0.10
        )
        
        # Overall Education Inflation - weighted by spending pattern
        # Parents spend most on school (12+ years), then college (3-5 years), then coaching
        overall_rate = (
            school_avg * 0.50 +        # School is longest duration
            higher_ed_avg * 0.30 +     # College/University
            coaching_avg * 0.20        # Coaching/Tuition
        )
        
        return {
            'cagr': round(overall_rate, 2),
            'best_estimate': round(overall_rate, 2),
            'total_inflation': round(((1 + overall_rate/100) ** 20 - 1) * 100, 2),
            'avg_yoy': round(overall_rate, 2),
            'period': '2005-2025',
            'years': 20,
            'data_source': 'Education Surveys (AISHE, NSSO, Industry Reports)',
            'description': 'Children education cost inflation (school + college + coaching)',
            'method_used': 'weighted_average',
            'data_points_used': len(df),
            'categories': {
                'school': {
                    'budget': round(budget_rate, 2),
                    'mid_range': round(mid_rate, 2),
                    'premium': round(premium_rate, 2),
                    'average': round(school_avg, 2),
                    'note': 'Annual school fees (tuition, books, uniform)'
                },
                'higher_education': {
                    **{k: round(v, 2) for k, v in higher_ed_rates.items()},
                    'average': round(higher_ed_avg, 2),
                    'note': 'Total program cost (3-5 years)'
                },
                'coaching': {
                    **{k: round(v, 2) for k, v in coaching_rates.items()},
                    'average': round(coaching_avg, 2),
                    'note': 'Annual coaching/tuition fees'
                }
            }
        }
    
    def get_inflation_rate(self, category: str) -> Optional[Dict]:
        """Get inflation rate for a specific category"""
        category_map = {
            'gold': 'gold',
            'house': 'real_estate',
            'real_estate': 'real_estate',
            'car': 'car',
            'vehicle': 'car',
            'education': 'education',
            'children_education': 'education'
        }
        
        mapped_category = category_map.get(category.lower())
        if mapped_category:
            return self._cached_rates.get(mapped_category)
        return None
    
    def get_all_inflation_rates(self) -> Dict:
        """Get all inflation rates"""
        return self._cached_rates
    
    def get_inflation_rate_simple(self, category: str) -> float:
        """Get just the CAGR value for a category (as decimal for calculations)"""
        rate_data = self.get_inflation_rate(category)
        if rate_data:
            return rate_data.get('cagr', 6.0) / 100
        return 0.06  # Default 6%
    
    def calculate_future_value(self, current_value: float, category: str, years: int) -> Dict:
        """Calculate inflation-adjusted future value"""
        inflation_rate = self.get_inflation_rate_simple(category)
        future_value = current_value * ((1 + inflation_rate) ** years)
        total_inflation = ((future_value - current_value) / current_value) * 100
        
        return {
            'current_value': round(current_value, 2),
            'future_value': round(future_value, 2),
            'years': years,
            'inflation_rate_used': round(inflation_rate * 100, 2),
            'total_inflation': round(total_inflation, 2),
            'category': category
        }


# Singleton instance for reuse
_inflation_provider: Optional[InflationRatesProvider] = None


def get_inflation_provider() -> InflationRatesProvider:
    """Get or create the inflation rates provider singleton"""
    global _inflation_provider
    if _inflation_provider is None:
        _inflation_provider = InflationRatesProvider()
    return _inflation_provider
