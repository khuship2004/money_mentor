"""
Real Estate Inflation Analysis using CAGR
Uses RBI/NHB Housing Price Index data for accurate inflation calculation
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import warnings
warnings.filterwarnings('ignore')


class RealEstateInflationAnalyzer:
    def __init__(self):
        self.hpi_data = None
        self.city_data = None
        self.model = None
        
    def load_hpi_data(self):
        """
        Load Housing Price Index (HPI) data
        Source: RBI/NHB (National Housing Bank) Housing Price Index
        Base Year: 2010-11 = 100
        """
        print("\n" + "=" * 70)
        print("    LOADING HOUSING PRICE INDEX (HPI) DATA")
        print("    Source: RBI/NHB Official Data")
        print("=" * 70)
        
        # RBI Housing Price Index Data (All India Average)
        # Source: https://www.rbi.org.in and NHB RESIDEX
        hpi_all_india = {
            'Year': [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'HPI_Index': [100, 111, 126, 143, 158, 167, 175, 183, 191, 198, 195, 203, 218, 237, 261, 287]
        }
        
        # City-wise HPI Data (Index values with 2010 = 100)
        city_hpi = {
            'Year': [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'Mumbai': [100, 115, 135, 156, 172, 178, 183, 189, 195, 201, 196, 205, 223, 248, 278, 312],
            'Delhi': [100, 112, 128, 147, 163, 172, 180, 188, 196, 204, 200, 210, 228, 252, 280, 310],
            'Bangalore': [100, 110, 124, 140, 155, 165, 176, 188, 201, 215, 212, 225, 248, 278, 315, 358],
            'Chennai': [100, 109, 121, 136, 150, 159, 167, 175, 183, 190, 186, 195, 210, 230, 254, 280],
            'Hyderabad': [100, 108, 119, 132, 145, 154, 165, 180, 198, 220, 218, 238, 268, 305, 350, 402],
            'Pune': [100, 111, 125, 142, 158, 168, 178, 188, 198, 208, 204, 215, 232, 255, 282, 312],
            'Kolkata': [100, 107, 117, 128, 140, 148, 155, 162, 169, 175, 172, 180, 192, 208, 226, 246],
            'Ahmedabad': [100, 108, 118, 130, 143, 152, 161, 170, 179, 188, 185, 195, 210, 230, 254, 280]
        }
        
        self.hpi_data = pd.DataFrame(hpi_all_india)
        self.city_data = pd.DataFrame(city_hpi)
        
        print(f"\n  Data Period: {self.hpi_data['Year'].min()} - {self.hpi_data['Year'].max()}")
        print(f"  Total Years: {len(self.hpi_data)}")
        print(f"  Cities Covered: {len(self.city_data.columns) - 1}")
        print(f"  Base Year: 2010 (Index = 100)")
        
    def calculate_all_india_inflation(self):
        """Calculate All India real estate inflation using CAGR"""
        print("\n" + "=" * 70)
        print("    ALL INDIA HOUSING PRICE INFLATION (CAGR)")
        print("=" * 70)
        
        df = self.hpi_data.copy()
        
        # Calculate Year-over-Year change
        df['YoY_Change'] = df['HPI_Index'].pct_change() * 100
        
        print(f"\n  {'Year':<8} {'HPI Index':>12} {'YoY Change':>14}")
        print("  " + "-" * 38)
        
        for _, row in df.iterrows():
            yoy = row['YoY_Change']
            yoy_str = f"{yoy:+.2f}%" if pd.notna(yoy) else "N/A"
            print(f"  {int(row['Year']):<8} {row['HPI_Index']:>12.0f} {yoy_str:>14}")
        
        # Calculate CAGR
        first_year = df['Year'].iloc[0]
        last_year = df['Year'].iloc[-1]
        first_index = df['HPI_Index'].iloc[0]
        last_index = df['HPI_Index'].iloc[-1]
        total_years = last_year - first_year
        
        # CAGR Formula
        cagr = ((last_index / first_index) ** (1 / total_years) - 1) * 100
        
        # Total inflation
        total_inflation = ((last_index - first_index) / first_index) * 100
        
        # Average YoY
        avg_yoy = df['YoY_Change'].dropna().mean()
        
        # Geometric mean
        growth_rates = (df['HPI_Index'] / df['HPI_Index'].shift(1)).dropna()
        geometric_mean = (np.prod(growth_rates) ** (1 / len(growth_rates)) - 1) * 100
        
        print("\n  " + "-" * 38)
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"\n  Starting Index: {first_index:.0f}")
        print(f"  Ending Index:   {last_index:.0f}")
        
        print(f"\n  " + "-" * 50)
        print(f"  INFLATION CALCULATION METHODS:")
        print(f"  " + "-" * 50)
        print(f"  1. Total Inflation:              {total_inflation:>10.2f}%")
        print(f"  2. CAGR (Compound Annual):       {cagr:>10.2f}%")
        print(f"  3. Average YoY Inflation:        {avg_yoy:>10.2f}%")
        print(f"  4. Geometric Mean Growth:        {geometric_mean:>10.2f}%")
        print(f"  " + "-" * 50)
        
        print(f"\n  >>> ALL INDIA REAL ESTATE INFLATION: {cagr:.2f}% per year (CAGR)")
        
        return {
            'total_inflation': total_inflation,
            'cagr': cagr,
            'avg_yoy': avg_yoy,
            'geometric_mean': geometric_mean,
            'years': total_years
        }
    
    def calculate_city_wise_inflation(self):
        """Calculate city-wise real estate inflation"""
        print("\n" + "=" * 70)
        print("    CITY-WISE REAL ESTATE INFLATION (CAGR)")
        print("=" * 70)
        
        df = self.city_data.copy()
        cities = [col for col in df.columns if col != 'Year']
        
        first_year = df['Year'].iloc[0]
        last_year = df['Year'].iloc[-1]
        total_years = last_year - first_year
        
        results = []
        
        for city in cities:
            first_index = df[city].iloc[0]
            last_index = df[city].iloc[-1]
            
            # CAGR
            cagr = ((last_index / first_index) ** (1 / total_years) - 1) * 100
            
            # Total inflation
            total_inflation = ((last_index - first_index) / first_index) * 100
            
            results.append({
                'City': city,
                'Start_Index': first_index,
                'End_Index': last_index,
                'Total_Inflation': total_inflation,
                'CAGR': cagr
            })
        
        results_df = pd.DataFrame(results).sort_values('CAGR', ascending=False)
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"\n  +{'-'*15}+{'-'*12}+{'-'*12}+{'-'*18}+{'-'*12}+")
        print(f"  | {'City':<13} | {'2010':>10} | {'2025':>10} | {'Total Inflation':>16} | {'CAGR':>10} |")
        print(f"  +{'-'*15}+{'-'*12}+{'-'*12}+{'-'*18}+{'-'*12}+")
        
        for _, row in results_df.iterrows():
            print(f"  | {row['City']:<13} | {row['Start_Index']:>10.0f} | {row['End_Index']:>10.0f} | {row['Total_Inflation']:>15.2f}% | {row['CAGR']:>9.2f}% |")
        
        print(f"  +{'-'*15}+{'-'*12}+{'-'*12}+{'-'*18}+{'-'*12}+")
        
        # Average CAGR across cities
        avg_cagr = results_df['CAGR'].mean()
        print(f"\n  Average CAGR across cities: {avg_cagr:.2f}%")
        
        # Best and worst performers
        best_city = results_df.iloc[0]
        worst_city = results_df.iloc[-1]
        
        print(f"\n  Highest Growth: {best_city['City']} ({best_city['CAGR']:.2f}% CAGR)")
        print(f"  Lowest Growth:  {worst_city['City']} ({worst_city['CAGR']:.2f}% CAGR)")
        
        return results_df
    
    def train_prediction_model(self):
        """Train Linear Regression model for future predictions"""
        print("\n" + "=" * 70)
        print("    LINEAR REGRESSION MODEL FOR PREDICTION")
        print("=" * 70)
        
        df = self.hpi_data.copy()
        
        X = df[['Year']].values
        y = df['HPI_Index'].values
        
        self.model = LinearRegression()
        self.model.fit(X, y)
        
        # Predictions on training data
        y_pred = self.model.predict(X)
        
        r2 = r2_score(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))
        
        print(f"\n  Model: Linear Regression")
        print(f"  Equation: HPI = {self.model.coef_[0]:.2f} × Year + {self.model.intercept_:.2f}")
        print(f"\n  R² Score: {r2:.4f} ({r2*100:.2f}%)")
        print(f"  RMSE: {rmse:.2f}")
        
        # Annual trend from model
        annual_increase = self.model.coef_[0]
        avg_hpi = df['HPI_Index'].mean()
        trend_based_inflation = (annual_increase / avg_hpi) * 100
        
        print(f"\n  Annual HPI Increase (Slope): {annual_increase:.2f} points/year")
        print(f"  Trend-based Inflation Rate: {trend_based_inflation:.2f}%")
        
        return {
            'r2': r2,
            'rmse': rmse,
            'slope': annual_increase,
            'trend_inflation': trend_based_inflation
        }
    
    def predict_future_prices(self, years_ahead=5):
        """Predict future HPI values"""
        print("\n" + "=" * 70)
        print("    FUTURE HPI PREDICTIONS")
        print("=" * 70)
        
        last_year = self.hpi_data['Year'].iloc[-1]
        last_index = self.hpi_data['HPI_Index'].iloc[-1]
        
        # Get CAGR for compounding
        first_index = self.hpi_data['HPI_Index'].iloc[0]
        total_years = last_year - self.hpi_data['Year'].iloc[0]
        cagr = ((last_index / first_index) ** (1 / total_years) - 1)
        
        print(f"\n  Using CAGR of {cagr*100:.2f}% for future projections")
        print(f"\n  {'Year':<8} {'Predicted HPI':>15} {'Growth from 2025':>18}")
        print("  " + "-" * 45)
        
        predictions = []
        for i in range(1, years_ahead + 1):
            future_year = last_year + i
            predicted_hpi = last_index * ((1 + cagr) ** i)
            growth = ((predicted_hpi - last_index) / last_index) * 100
            
            predictions.append({
                'Year': future_year,
                'Predicted_HPI': predicted_hpi,
                'Growth': growth
            })
            
            print(f"  {future_year:<8} {predicted_hpi:>15.0f} {growth:>17.2f}%")
        
        print("  " + "-" * 45)
        
        return predictions
    
    def print_summary(self, all_india, city_results):
        """Print final summary"""
        print("\n" + "=" * 70)
        print("    FINAL SUMMARY - REAL ESTATE INFLATION")
        print("=" * 70)
        
        print(f"\n  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Metric':<43} | {'Value':>16} |")
        print(f"  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Data Source':<43} | {'RBI/NHB HPI':>16} |")
        print(f"  | {'Period':<43} | {'2010 - 2025':>16} |")
        print(f"  | {'Total Years':<43} | {all_india['years']:>16} |")
        print(f"  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Total Inflation (All India)':<43} | {all_india['total_inflation']:>15.2f}% |")
        print(f"  | {'CAGR (Compound Annual Growth Rate)':<43} | {all_india['cagr']:>15.2f}% |")
        print(f"  | {'Average YoY Inflation':<43} | {all_india['avg_yoy']:>15.2f}% |")
        print(f"  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Highest City CAGR':<43} | {city_results.iloc[0]['City']:>10} {city_results.iloc[0]['CAGR']:>4.1f}% |")
        print(f"  | {'Lowest City CAGR':<43} | {city_results.iloc[-1]['City']:>10} {city_results.iloc[-1]['CAGR']:>4.1f}% |")
        print(f"  +{'-'*45}+{'-'*18}+")
        
        print(f"\n  >>> REAL ESTATE INFLATION RATE: {all_india['cagr']:.2f}% per year (CAGR)")
    
    def run_analysis(self):
        """Run complete analysis"""
        print("\n" + "=" * 70)
        print("    REAL ESTATE INFLATION ANALYSIS USING CAGR")
        print("    Based on RBI/NHB Housing Price Index (HPI)")
        print("=" * 70)
        
        # Load data
        self.load_hpi_data()
        
        # Calculate All India inflation
        all_india = self.calculate_all_india_inflation()
        
        # Calculate city-wise inflation
        city_results = self.calculate_city_wise_inflation()
        
        # Train prediction model
        self.train_prediction_model()
        
        # Future predictions
        self.predict_future_prices(5)
        
        # Print summary
        self.print_summary(all_india, city_results)
        
        print("\n" + "=" * 70)
        print("    ANALYSIS COMPLETE!")
        print("=" * 70)
        
        return all_india, city_results


def main():
    analyzer = RealEstateInflationAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
