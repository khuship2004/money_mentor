"""
Gold Inflation Analysis with Linear Regression
Analyzes gold price trends and calculates inflation rates
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class GoldInflationAnalyzer:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.gold_data = None
        self.model = None
        self.yearly_data = None
        
    def load_data(self):
        """Load gold data from Excel"""
        print("\n" + "=" * 70)
        print("    LOADING GOLD DATA FROM EXCEL")
        print("=" * 70)
        
        self.gold_data = pd.read_excel(self.excel_path, sheet_name='Gold_Data')
        self.gold_data['Date'] = pd.to_datetime(self.gold_data['Date'])
        self.gold_data = self.gold_data.sort_values('Date').reset_index(drop=True)
        
        print(f"\n  Total Records: {len(self.gold_data)}")
        print(f"  Date Range: {self.gold_data['Date'].min().strftime('%Y-%m-%d')} to {self.gold_data['Date'].max().strftime('%Y-%m-%d')}")
        print(f"  Columns: {list(self.gold_data.columns)}")
        
    def calculate_yearly_inflation(self):
        """Calculate year-by-year inflation rates"""
        print("\n" + "=" * 70)
        print("    YEARLY GOLD PRICES & INFLATION RATES")
        print("=" * 70)
        
        df = self.gold_data.copy()
        df['Year'] = df['Date'].dt.year
        
        # Aggregate yearly data
        yearly = df.groupby('Year')['Price'].agg(['mean', 'first', 'last', 'min', 'max', 'std']).reset_index()
        yearly.columns = ['Year', 'Avg_Price', 'Start_Price', 'End_Price', 'Min_Price', 'Max_Price', 'Volatility']
        
        # Calculate Year-over-Year inflation
        yearly['YoY_Inflation'] = yearly['Avg_Price'].pct_change() * 100
        
        # Print table
        print(f"\n  {'Year':<6} {'Avg Price':>14} {'Min':>12} {'Max':>12} {'YoY Inflation':>15}")
        print("  " + "-" * 62)
        
        for _, row in yearly.iterrows():
            yoy = row['YoY_Inflation']
            yoy_str = f"{yoy:+.2f}%" if pd.notna(yoy) else "N/A"
            print(f"  {int(row['Year']):<6} Rs.{row['Avg_Price']:>10,.0f} Rs.{row['Min_Price']:>8,.0f} Rs.{row['Max_Price']:>8,.0f} {yoy_str:>15}")
        
        print("  " + "-" * 62)
        
        self.yearly_data = yearly
        return yearly
    
    def calculate_overall_inflation(self):
        """Calculate overall inflation using multiple methods"""
        print("\n" + "=" * 70)
        print("    OVERALL GOLD INFLATION CALCULATION")
        print("=" * 70)
        
        yearly = self.yearly_data
        
        # Method 1: Simple Total Inflation
        first_price = yearly['Avg_Price'].iloc[0]
        last_price = yearly['Avg_Price'].iloc[-1]
        first_year = yearly['Year'].iloc[0]
        last_year = yearly['Year'].iloc[-1]
        total_years = last_year - first_year
        
        total_inflation = ((last_price - first_price) / first_price) * 100
        
        # Method 2: CAGR (Compound Annual Growth Rate)
        cagr = ((last_price / first_price) ** (1 / total_years) - 1) * 100
        
        # Method 3: Average of YoY Inflations
        valid_yoy = yearly['YoY_Inflation'].dropna()
        avg_yoy_inflation = valid_yoy.mean()
        
        # Method 4: Geometric Mean of Growth Rates
        growth_rates = (yearly['Avg_Price'] / yearly['Avg_Price'].shift(1)).dropna()
        geometric_mean = (np.prod(growth_rates) ** (1 / len(growth_rates)) - 1) * 100
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"\n  Starting Price (Avg {first_year}): Rs. {first_price:,.2f}")
        print(f"  Ending Price (Avg {last_year}):   Rs. {last_price:,.2f}")
        
        print(f"\n  " + "-" * 50)
        print(f"  INFLATION CALCULATION METHODS:")
        print(f"  " + "-" * 50)
        print(f"  1. Total Inflation:              {total_inflation:>10.2f}%")
        print(f"  2. CAGR (Compound Annual):       {cagr:>10.2f}%")
        print(f"  3. Average YoY Inflation:        {avg_yoy_inflation:>10.2f}%")
        print(f"  4. Geometric Mean Growth:        {geometric_mean:>10.2f}%")
        print(f"  " + "-" * 50)
        
        # Best estimate (CAGR is most commonly used)
        print(f"\n  >>> OVERALL ANNUAL INFLATION RATE: {cagr:.2f}% per year")
        
        return {
            'total_inflation': total_inflation,
            'cagr': cagr,
            'avg_yoy': avg_yoy_inflation,
            'geometric_mean': geometric_mean,
            'years': total_years
        }
    
    def train_linear_regression(self):
        """Train Linear Regression to model price trends"""
        print("\n" + "=" * 70)
        print("    LINEAR REGRESSION MODEL TRAINING")
        print("=" * 70)
        
        df = self.gold_data.copy()
        
        # Create features
        df['Days_From_Start'] = (df['Date'] - df['Date'].min()).dt.days
        df['Year'] = df['Date'].dt.year
        df['Month'] = df['Date'].dt.month
        df['DayOfYear'] = df['Date'].dt.dayofyear
        
        # Lag features
        for lag in [1, 7, 30]:
            df[f'Price_Lag_{lag}'] = df['Price'].shift(lag)
        
        # Moving averages
        df['MA_7'] = df['Price'].rolling(7).mean()
        df['MA_30'] = df['Price'].rolling(30).mean()
        
        df = df.dropna()
        
        # Features and target
        feature_cols = ['Days_From_Start', 'Year', 'Month', 'DayOfYear', 
                       'Price_Lag_1', 'Price_Lag_7', 'Price_Lag_30', 'MA_7', 'MA_30']
        X = df[feature_cols]
        y = df['Price']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.model = LinearRegression()
        self.model.fit(X_train, y_train)
        
        # Predictions
        y_pred = self.model.predict(X_test)
        
        # Metrics
        r2 = r2_score(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"\n  Training samples: {len(X_train)}")
        print(f"  Testing samples:  {len(X_test)}")
        
        print(f"\n  " + "-" * 40)
        print(f"  MODEL PERFORMANCE:")
        print(f"  " + "-" * 40)
        print(f"  R² Score:     {r2:.4f} ({r2*100:.2f}%)")
        print(f"  RMSE:         Rs. {rmse:,.2f}")
        print(f"  MAE:          Rs. {mae:,.2f}")
        print(f"  " + "-" * 40)
        
        # Feature importance (coefficients)
        print(f"\n  Feature Importance (Coefficients):")
        coef_df = pd.DataFrame({
            'Feature': feature_cols,
            'Coefficient': self.model.coef_
        }).sort_values('Coefficient', key=abs, ascending=False)
        
        for _, row in coef_df.iterrows():
            print(f"    {row['Feature']:<20}: {row['Coefficient']:>12.4f}")
        
        # Calculate trend from model
        # Daily growth rate from Days_From_Start coefficient
        daily_growth = self.model.coef_[0]  # Coefficient for Days_From_Start
        annual_growth_from_model = daily_growth * 365
        
        print(f"\n  >>> MODEL'S ESTIMATED DAILY TREND: Rs. {daily_growth:.2f}/day")
        print(f"  >>> MODEL'S ESTIMATED ANNUAL TREND: Rs. {annual_growth_from_model:,.2f}/year")
        
        return {
            'r2': r2,
            'rmse': rmse,
            'mae': mae,
            'daily_trend': daily_growth,
            'annual_trend': annual_growth_from_model
        }
    
    def calculate_inflation_from_trend(self):
        """Calculate inflation rate from the linear trend"""
        print("\n" + "=" * 70)
        print("    INFLATION RATE FROM LINEAR REGRESSION TREND")
        print("=" * 70)
        
        yearly = self.yearly_data
        
        # Fit a simple linear regression on yearly averages
        X_years = yearly['Year'].values.reshape(-1, 1)
        y_prices = yearly['Avg_Price'].values
        
        model = LinearRegression()
        model.fit(X_years, y_prices)
        
        slope = model.coef_[0]  # Price increase per year
        intercept = model.intercept_
        
        # Calculate inflation rate as percentage of average price
        avg_price = yearly['Avg_Price'].mean()
        inflation_rate = (slope / avg_price) * 100
        
        # Alternative: inflation relative to starting price
        first_price = yearly['Avg_Price'].iloc[0]
        inflation_from_start = (slope / first_price) * 100
        
        print(f"\n  Linear Trend Equation:")
        print(f"    Price = {slope:.2f} * Year + {intercept:.2f}")
        
        print(f"\n  Annual Price Increase (Slope): Rs. {slope:,.2f}/year")
        
        print(f"\n  " + "-" * 50)
        print(f"  INFLATION RATE CALCULATIONS:")
        print(f"  " + "-" * 50)
        print(f"  Based on Average Price:   {inflation_rate:.2f}% per year")
        print(f"  Based on Starting Price:  {inflation_from_start:.2f}% per year")
        print(f"  " + "-" * 50)
        
        # Predict next year's price
        next_year = yearly['Year'].iloc[-1] + 1
        predicted_price = model.predict([[next_year]])[0]
        
        print(f"\n  Predicted Price for {next_year}: Rs. {predicted_price:,.2f}")
        
        return {
            'slope': slope,
            'intercept': intercept,
            'inflation_from_avg': inflation_rate,
            'inflation_from_start': inflation_from_start,
            'next_year_prediction': predicted_price
        }
    
    def print_summary_table(self):
        """Print a formatted summary table"""
        print("\n" + "=" * 70)
        print("    GOLD INFLATION SUMMARY TABLE")
        print("=" * 70)
        
        yearly = self.yearly_data
        
        print(f"\n  +{'-'*8}+{'-'*16}+{'-'*16}+{'-'*18}+")
        print(f"  | {'Year':^6} | {'Avg Price':^14} | {'Change':^14} | {'YoY Inflation':^16} |")
        print(f"  +{'-'*8}+{'-'*16}+{'-'*16}+{'-'*18}+")
        
        prev_price = None
        for _, row in yearly.iterrows():
            year = int(row['Year'])
            price = row['Avg_Price']
            yoy = row['YoY_Inflation']
            
            if prev_price:
                change = price - prev_price
                change_str = f"Rs. {change:+,.0f}"
            else:
                change_str = "N/A"
            
            yoy_str = f"{yoy:+.2f}%" if pd.notna(yoy) else "N/A"
            
            print(f"  | {year:^6} | Rs. {price:>10,.0f} | {change_str:^14} | {yoy_str:^16} |")
            prev_price = price
        
        print(f"  +{'-'*8}+{'-'*16}+{'-'*16}+{'-'*18}+")
    
    def run_analysis(self):
        """Run complete analysis"""
        print("\n" + "=" * 70)
        print("=" * 70)
        print("    GOLD INFLATION ANALYSIS WITH LINEAR REGRESSION")
        print("=" * 70)
        print("=" * 70)
        
        # Load data
        self.load_data()
        
        # Calculate yearly inflation
        self.calculate_yearly_inflation()
        
        # Print summary table
        self.print_summary_table()
        
        # Calculate overall inflation
        inflation = self.calculate_overall_inflation()
        
        # Train Linear Regression
        model_results = self.train_linear_regression()
        
        # Calculate inflation from trend
        trend_inflation = self.calculate_inflation_from_trend()
        
        # Final Summary
        print("\n" + "=" * 70)
        print("    FINAL RESULTS")
        print("=" * 70)
        
        print(f"\n  +{'-'*40}+{'-'*15}+")
        print(f"  | {'Metric':<38} | {'Value':^13} |")
        print(f"  +{'-'*40}+{'-'*15}+")
        print(f"  | {'Total Inflation (2014-2026)':<38} | {inflation['total_inflation']:>10.2f}%  |")
        print(f"  | {'CAGR (Compound Annual Growth Rate)':<38} | {inflation['cagr']:>10.2f}%  |")
        print(f"  | {'Average YoY Inflation':<38} | {inflation['avg_yoy']:>10.2f}%  |")
        print(f"  | {'Trend-based Inflation Rate':<38} | {trend_inflation['inflation_from_avg']:>10.2f}%  |")
        print(f"  +{'-'*40}+{'-'*15}+")
        print(f"  | {'Linear Regression R² Score':<38} | {model_results['r2']*100:>10.2f}%  |")
        print(f"  | {'Model RMSE':<38} | Rs.{model_results['rmse']:>8,.0f}  |")
        print(f"  +{'-'*40}+{'-'*15}+")
        
        print(f"\n  >>> OVERALL GOLD INFLATION: {inflation['cagr']:.2f}% per year (CAGR)")
        
        print("\n" + "=" * 70)
        print("    ANALYSIS COMPLETE!")
        print("=" * 70)


def main():
    excel_path = r"c:\Users\Mahina Varma\OneDrive\Desktop\BE Project Datasets\BE Project Implementation\money_mentor\src\combined_dataset_20251005_175959.xlsx"
    
    analyzer = GoldInflationAnalyzer(excel_path)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
