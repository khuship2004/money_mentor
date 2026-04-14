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
        """Calculate car price inflation using BrandWise dataset.

        Uses the Brand_Avg_Price sheet from Car_Dataset_BrandWise.xlsx to
        compute both overall car inflation (all brands combined) and
        brand-wise year-on-year inflation (Hyundai, Mercedes, etc.).
        """
        try:
            # Use the same dataset as the standalone BrandWiseCarInflationAnalyzer
            car_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "Inflation Models",
                "Car_Dataset_BrandWise.xlsx",
            )

            # Brand-wise average prices with years as columns (2015-2025).
            # The workbook has title rows before the actual header row.
            brand_data = pd.read_excel(
                car_file,
                sheet_name="Brand_Avg_Price",
                header=2,
            )

            # Normalize column names to avoid hidden/extra whitespace issues.
            brand_data.columns = [str(col).strip() for col in brand_data.columns]

            # Clean brand data similar to BrandWiseCarInflationAnalyzer
            if "Brand" not in brand_data.columns or "Tier" not in brand_data.columns:
                raise ValueError("Required columns 'Brand' and 'Tier' not found in car brand dataset")

            df = brand_data.dropna(subset=["Brand", "Tier"]).copy()

            # Identify year columns (should be 2015-2025, numeric or string)
            year_cols_raw = [
                col
                for col in df.columns
                if isinstance(col, (int, float))
                or (isinstance(col, str) and col.replace(".0", "").isdigit())
            ]
            year_cols_raw = sorted(
                [col for col in year_cols_raw if 2015 <= float(col) <= 2025],
                key=lambda c: float(c),
            )

            if not year_cols_raw:
                raise ValueError("No yearly price columns found in car brand dataset")

            # Map columns to string year labels for JSON keys
            year_labels = [str(int(float(c))) for c in year_cols_raw]

            # Overall average price across all brands each year
            yearly_prices = df[year_cols_raw].mean()
            yearly_df = pd.DataFrame(
                {
                    "Year": [int(float(c)) for c in year_cols_raw],
                    "Avg_Price": yearly_prices.values,
                }
            )

            # Use comprehensive calculation with ALL methods for overall car inflation
            results = self._calculate_all_methods(yearly_df, "Avg_Price")

            # --- Brand-wise year-on-year inflation ---
            brand_yoy: Dict[str, Dict[str, float]] = {}
            df["Brand"] = df["Brand"].astype(str).str.strip()
            brand_df = df[df["Brand"] != ""].copy()

            for brand in sorted(brand_df["Brand"].unique()):
                rows = brand_df[brand_df["Brand"] == brand]
                if rows.empty:
                    continue

                # Average price per year for this brand
                brand_prices = rows[year_cols_raw].mean()

                # Compute YoY inflation for each consecutive year pair
                yoy_series: Dict[str, float] = {}
                for i in range(1, len(year_cols_raw)):
                    prev_col = year_cols_raw[i - 1]
                    curr_col = year_cols_raw[i]

                    prev_price = float(brand_prices.get(prev_col, np.nan))
                    curr_price = float(brand_prices.get(curr_col, np.nan))

                    if not (np.isfinite(prev_price) and np.isfinite(curr_price)) or prev_price <= 0:
                        continue

                    yoy = ((curr_price - prev_price) / prev_price) * 100.0
                    year_label = year_labels[i]
                    yoy_series[year_label] = round(float(yoy), 2)

                if yoy_series:
                    brand_yoy[brand] = yoy_series

            # Attach metadata and brand-wise YoY breakdown for UI consumption
            results["data_source"] = "Car Dataset BrandWise - Brand_Avg_Price (All Methods)"
            results["description"] = (
                "Brand-wise new vehicle price inflation using Brand_Avg_Price sheet "
                "with multiple calculation methods"
            )
            results["method_used"] = "best_estimate"
            if brand_yoy:
                results["brand_yoy"] = brand_yoy

            return results
        except Exception as e:
            print(f"Error calculating car inflation: {e}")
            return self._get_default_rates()["car"]
    
    def _calculate_education_inflation(self) -> Dict:
        """
        Calculate education inflation for children's education planning.
        Uses Inflation Models/India_Education_Inflation_Dataset_2005_2025_Combined.xlsx.
        """
        try:
            education_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "Inflation Models",
                "India_Education_Inflation_Dataset_2005_2025_Combined.xlsx",
            )

            summary_df = pd.read_excel(education_file, sheet_name="Summary_Stats", header=1)
            annual_df = pd.read_excel(education_file, sheet_name="Annual_YoY_Rates", header=1)

            summary_df.columns = [str(col).strip() for col in summary_df.columns]
            annual_df.columns = [str(col).strip() for col in annual_df.columns]

            summary_df = summary_df.rename(
                columns={
                    summary_df.columns[0]: "category",
                    summary_df.columns[1]: "key",
                    summary_df.columns[2]: "avg_yoy",
                    summary_df.columns[3]: "cagr",
                    summary_df.columns[4]: "total_inflation",
                }
            )

            summary_df = summary_df[summary_df["key"].notna()].copy()
            summary_df["key"] = summary_df["key"].astype(str).str.strip()
            summary_df["cagr"] = pd.to_numeric(summary_df["cagr"], errors="coerce")
            summary_df["avg_yoy"] = pd.to_numeric(summary_df["avg_yoy"], errors="coerce")

            metric_map = {
                row["key"]: {
                    "cagr": float(row["cagr"]),
                    "avg_yoy": float(row["avg_yoy"]) if pd.notna(row["avg_yoy"]) else float(row["cagr"]),
                }
                for _, row in summary_df.iterrows()
                if pd.notna(row["cagr"])
            }

            required_keys = [
                "School_Budget",
                "School_Mid_Range",
                "School_Premium",
                "HE_Govt_College",
                "HE_Private_College",
                "HE_Engineering",
                "HE_Medical",
                "HE_MBA",
                "Coaching_School_Tuition",
                "Coaching_IIT_JEE",
                "Coaching_NEET",
                "Coaching_UPSC",
            ]
            missing = [k for k in required_keys if k not in metric_map]
            if missing:
                raise ValueError(f"Missing required education metrics in Summary_Stats: {missing}")

            school_rates = {
                "budget": metric_map["School_Budget"]["cagr"],
                "mid_range": metric_map["School_Mid_Range"]["cagr"],
                "premium": metric_map["School_Premium"]["cagr"],
            }
            school_avg = float(np.mean(list(school_rates.values())))

            higher_ed_rates = {
                "govt_college": metric_map["HE_Govt_College"]["cagr"],
                "private_college": metric_map["HE_Private_College"]["cagr"],
                "engineering": metric_map["HE_Engineering"]["cagr"],
                "medical": metric_map["HE_Medical"]["cagr"],
                "mba": metric_map["HE_MBA"]["cagr"],
            }
            higher_ed_avg = float(np.mean(list(higher_ed_rates.values())))

            coaching_rates = {
                "school_tuition": metric_map["Coaching_School_Tuition"]["cagr"],
                "iit_jee": metric_map["Coaching_IIT_JEE"]["cagr"],
                "neet": metric_map["Coaching_NEET"]["cagr"],
                "upsc": metric_map["Coaching_UPSC"]["cagr"],
            }
            coaching_avg = float(np.mean(list(coaching_rates.values())))

            # Keep same household spending weights for overall estimate.
            overall_rate = school_avg * 0.50 + higher_ed_avg * 0.30 + coaching_avg * 0.20

            year_col = annual_df.columns[0]
            annual_df = annual_df[pd.to_numeric(annual_df[year_col], errors="coerce").notna()].copy()
            annual_df["Year"] = pd.to_numeric(annual_df[year_col], errors="coerce").astype(int)
            first_year = int(annual_df["Year"].min())
            last_year = int(annual_df["Year"].max())
            total_years = max(last_year - first_year, 1)

            # International Higher Education (for Indian students going abroad)
            # This workbook is India-focused, so keep existing international assumptions.
            international_rates = {
                "usa": {
                    "public_university": 9.82,
                    "private_ivy_league": 9.50,
                    "community_college": 10.24,
                    "average": 9.66,
                },
                "uk": {
                    "russell_group": 9.75,
                    "standard_university": 9.59,
                    "average": 9.67,
                },
                "germany": {
                    "public_free_tuition": 7.11,
                    "private_university": 9.35,
                    "average": 8.23,
                },
                "canada": {
                    "top_universities": 9.30,
                    "standard": 9.88,
                    "average": 9.59,
                },
                "australia": {
                    "group_of_eight": 7.97,
                    "standard": 8.34,
                    "average": 8.16,
                },
            }
            international_avg = (
                international_rates["usa"]["average"] * 0.35
                + international_rates["uk"]["average"] * 0.20
                + international_rates["germany"]["average"] * 0.15
                + international_rates["canada"]["average"] * 0.20
                + international_rates["australia"]["average"] * 0.10
            )

            program_costs_2025 = {
                "usa_public": 41.0,
                "usa_private": 80.3,
                "uk_russell": 51.6,
                "uk_standard": 39.2,
                "germany_public": 15.3,
                "canada_top": 47.1,
                "australia_go8": 42.6,
            }

            return {
                "cagr": round(overall_rate, 2),
                "best_estimate": round(overall_rate, 2),
                "total_inflation": round(((1 + overall_rate / 100) ** total_years - 1) * 100, 2),
                "avg_yoy": round(overall_rate, 2),
                "period": f"{first_year}-{last_year}",
                "years": total_years,
                "data_source": "India_Education_Inflation_Dataset_2005_2025_Combined.xlsx",
                "description": "Children education cost inflation from combined education dataset",
                "method_used": "weighted_average",
                "data_points_used": len(annual_df),
                "categories": {
                    "school": {
                        **{k: round(v, 2) for k, v in school_rates.items()},
                        "average": round(school_avg, 2),
                        "note": "CAGR from Summary_Stats sheet",
                    },
                    "higher_education": {
                        **{k: round(v, 2) for k, v in higher_ed_rates.items()},
                        "average": round(higher_ed_avg, 2),
                        "note": "CAGR from Summary_Stats sheet",
                    },
                    "coaching": {
                        **{k: round(v, 2) for k, v in coaching_rates.items()},
                        "average": round(coaching_avg, 2),
                        "note": "CAGR from Summary_Stats sheet",
                    },
                    "international": {
                    'usa': {
                        'public': round(international_rates['usa']['public_university'], 2),
                        'private_ivy': round(international_rates['usa']['private_ivy_league'], 2),
                        'average': round(international_rates['usa']['average'], 2),
                        'cost_per_year_lakhs': program_costs_2025['usa_public'],
                        'cost_private_lakhs': program_costs_2025['usa_private']
                    },
                    'uk': {
                        'russell_group': round(international_rates['uk']['russell_group'], 2),
                        'standard': round(international_rates['uk']['standard_university'], 2),
                        'average': round(international_rates['uk']['average'], 2),
                        'cost_per_year_lakhs': program_costs_2025['uk_russell']
                    },
                    'germany': {
                        'public_free_tuition': round(international_rates['germany']['public_free_tuition'], 2),
                        'private': round(international_rates['germany']['private_university'], 2),
                        'average': round(international_rates['germany']['average'], 2),
                        'cost_per_year_lakhs': program_costs_2025['germany_public'],
                        'note': 'Public universities have FREE tuition - only living costs'
                    },
                    'canada': {
                        'top_universities': round(international_rates['canada']['top_universities'], 2),
                        'standard': round(international_rates['canada']['standard'], 2),
                        'average': round(international_rates['canada']['average'], 2),
                        'cost_per_year_lakhs': program_costs_2025['canada_top']
                    },
                    'australia': {
                        'group_of_eight': round(international_rates['australia']['group_of_eight'], 2),
                        'standard': round(international_rates['australia']['standard'], 2),
                        'average': round(international_rates['australia']['average'], 2),
                        'cost_per_year_lakhs': program_costs_2025['australia_go8']
                    },
                    'average': round(international_avg, 2),
                    'note': 'Inflation for Indian students (includes INR depreciation)',
                    'period': '2010-2025',
                    'program_durations': {
                        'masters_mba': '2 years',
                        'undergraduate': '4 years',
                        'ug_plus_pg': '6 years (After 10th to PG)'
                    }
                }
                },
            }
        except Exception as e:
            print(f"Error calculating education inflation from Excel: {e}")
            return self._get_default_rates()["education"]
    
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
