"""
Car Price Inflation Analysis using BrandWise Dataset
Analyzes car price trends by brand and segment
Based on Brand_Avg_Price and Segment_Avg_Price sheets
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class BrandWiseCarInflationAnalyzer:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.brand_data = None
        self.segment_data = None
        self.models = {}
        self.results = {}
        
    def load_data(self):
        """Load car data from BrandWise Excel sheets"""
        print("\n" + "=" * 80)
        print("    LOADING CAR DATA FROM BRANDWISE DATASET")
        print("=" * 80)
        
        # Read Brand_Avg_Price sheet (header at row 1)
        self.brand_data = pd.read_excel(
            self.excel_path, 
            sheet_name='Brand_Avg_Price',
            header=1  # Use row 1 as header
        )
        
        # Read Segment_Avg_Price sheet
        self.segment_data = pd.read_excel(
            self.excel_path,
            sheet_name='Segment_Avg_Price',
            header=1
        )
        
        print(f"\n  Brand_Avg_Price Records: {len(self.brand_data)}")
        print(f"  Columns: {list(self.brand_data.columns[:8])}")
        
        print(f"\n  Segment_Avg_Price Records: {len(self.segment_data)}")
        print(f"  Columns: {list(self.segment_data.columns[:8])}")
        
    def clean_brand_data(self):
        """Clean and prepare brand data"""
        print("\n" + "=" * 80)
        print("    DATA CLEANING & PREPARATION")
        print("=" * 80)
        
        df = self.brand_data.copy()
        
        # Remove rows with NaN values in critical columns
        df = df.dropna(subset=['Brand', 'Tier'])
        
        # Get year columns (should be 2015-2025)
        year_cols = [col for col in df.columns if isinstance(col, (int, float)) or (isinstance(col, str) and col.replace('.0', '').isdigit())]
        year_cols = sorted([col for col in year_cols if 2015 <= float(col) <= 2025], key=float)
        
        print(f"\n  [1] Cleaned brand data: {len(df)} brands with tier information")
        print(f"  [2] Year columns identified: {[int(float(y)) for y in year_cols]}")
        print(f"  [3] Brands included:")
        
        for idx, row in df.iterrows():
            brand = row['Brand']
            tier = row['Tier']
            if pd.notna(brand) and pd.notna(tier):
                print(f"      - {brand} ({tier})")
        
        self.brand_data_clean = df
        self.year_columns = year_cols
        return df, year_cols
    
    def calculate_brand_inflation(self):
        """Calculate inflation rate for each brand"""
        print("\n" + "=" * 80)
        print("    BRAND-WISE INFLATION ANALYSIS")
        print("=" * 80)
        
        df = self.brand_data_clean
        year_cols = self.year_columns
        
        inflation_results = []
        
        print(f"\n  {'Brand':<20} {'Tier':<15} {'2015':<10} {'2025':<10} {'CAGR':<10}")
        print("  " + "-" * 70)
        
        for idx, row in df.iterrows():
            brand = row['Brand']
            tier = row['Tier']
            
            if pd.isna(brand) or pd.isna(tier):
                continue
            
            # Get prices for 2015 and latest available year
            prices = [row.get(col) for col in year_cols if pd.notna(row.get(col))]
            
            if len(prices) < 2:
                continue
            
            first_price = prices[0]
            last_price = prices[-1]
            years_span = len(prices) - 1
            
            # Calculate CAGR
            if first_price > 0 and years_span > 0:
                cagr = ((last_price / first_price) ** (1 / years_span) - 1) * 100
            else:
                cagr = 0
            
            inflation_results.append({
                'Brand': brand,
                'Tier': tier,
                'First_Price': first_price,
                'Last_Price': last_price,
                'CAGR': cagr
            })
            
            print(f"  {brand:<20} {tier:<15} {first_price:<10.2f} {last_price:<10.2f} {cagr:<10.2f}%")
        
        self.inflation_results = pd.DataFrame(inflation_results)
        return pd.DataFrame(inflation_results)
    
    def prepare_features_for_ml(self):
        """Prepare features for ML models"""
        print("\n" + "=" * 80)
        print("    FEATURE ENGINEERING FOR ML MODELS")
        print("=" * 80)
        
        df = self.brand_data_clean.copy()
        year_cols = self.year_columns
        
        # Create a dataset with one row per brand-year combination
        ml_data = []
        
        for idx, row in df.iterrows():
            brand = row['Brand']
            tier = row['Tier']
            
            if pd.isna(brand) or pd.isna(tier):
                continue
            
            # Encode tier
            tier_encoded = 1 if tier == 'Mass Market' else 2
            
            for year_col in year_cols:
                price = row.get(year_col)
                if pd.notna(price) and price > 0:
                    year = int(float(year_col))
                    years_from_start = year - 2015
                    
                    ml_data.append({
                        'Year': year,
                        'Price': price,
                        'Tier': tier_encoded,
                        'Years_From_Start': years_from_start
                    })
        
        X = pd.DataFrame(ml_data)[['Year', 'Tier', 'Years_From_Start']]
        y = pd.DataFrame(ml_data)['Price']
        
        print(f"\n  Total data points: {len(X)}")
        print(f"  Features: Year, Tier, Years_From_Start")
        print(f"  Target: Price")
        print(f"  Data shape: {X.shape}")
        
        return X, y
    
    def train_ml_models(self, X, y):
        """Train ML models for price prediction"""
        print("\n" + "=" * 80)
        print("    TRAINING ML MODELS")
        print("=" * 80)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Models
        models = {
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
            'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
        }
        
        print(f"\n  Training size: {len(X_train)}, Test size: {len(X_test)}")
        print(f"\n  +{'-'*25}+{'-'*12}+{'-'*15}+{'-'*15}+")
        print(f"  | {'Model':<23} | {'R² Score':>10} | {'RMSE':>13} | {'MAE':>13} |")
        print(f"  +{'-'*25}+{'-'*12}+{'-'*15}+{'-'*15}+")
        
        for name, model in models.items():
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
            
            r2 = r2_score(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            mae = mean_absolute_error(y_test, y_pred)
            
            self.results[name] = {
                'r2_score': r2,
                'rmse': rmse,
                'mae': mae,
                'model': model,
                'scaler': scaler
            }
            
            print(f"  | {name:<23} | {r2*100:>9.2f}% | {rmse:>12.2f} | {mae:>12.2f} |")
        
        print(f"  +{'-'*25}+{'-'*12}+{'-'*15}+{'-'*15}+")
        
        return X_test, y_test
    
    def find_best_model(self):
        """Find and display best model"""
        print("\n" + "=" * 80)
        print("    BEST MODEL ANALYSIS")
        print("=" * 80)
        
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['r2_score'], reverse=True)
        
        best_name, best_metrics = sorted_results[0]
        
        print(f"\n  Best Model: {best_name}")
        print(f"  R² Score: {best_metrics['r2_score']*100:.2f}%")
        print(f"  RMSE: {best_metrics['rmse']:.2f}")
        print(f"  MAE: {best_metrics['mae']:.2f}")
        
        return best_name, best_metrics
    
    def print_summary(self):
        """Print final summary"""
        print("\n" + "=" * 80)
        print("    FINAL SUMMARY - CAR INFLATION ANALYSIS (BRANDWISE)")
        print("=" * 80)
        
        inflation_df = self.inflation_results
        
        print(f"\n  Total Brands Analyzed: {len(inflation_df)}")
        print(f"  Period: 2015 - 2025")
        
        print(f"\n  Average CAGR across all brands: {inflation_df['CAGR'].mean():.2f}%")
        print(f"  Highest CAGR: {inflation_df['CAGR'].max():.2f}% ({inflation_df.loc[inflation_df['CAGR'].idxmax(), 'Brand']})")
        print(f"  Lowest CAGR: {inflation_df['CAGR'].min():.2f}% ({inflation_df.loc[inflation_df['CAGR'].idxmin(), 'Brand']})")
        
        print(f"\n  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Metric':<43} | {'Value':^16} |")
        print(f"  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Dataset':<43} | {'Car_Dataset_BrandWise':>16} |")
        print(f"  | {'Brands Analyzed':<43} | {len(inflation_df):>16} |")
        print(f"  | {'Average Inflation (CAGR)':<43} | {inflation_df['CAGR'].mean():>15.2f}% |")
        print(f"  +{'-'*45}+{'-'*18}+")
        
        best_name = max(self.results.items(), key=lambda x: x[1]['r2_score'])[0]
        best_r2 = max(self.results.items(), key=lambda x: x[1]['r2_score'])[1]['r2_score']
        
        print(f"\n  Best Prediction Model: {best_name}")
        print(f"  Model Accuracy (R²): {best_r2*100:.2f}%")
    
    def run_analysis(self):
        """Run complete analysis"""
        print("\n" + "=" * 80)
        print("=" * 80)
        print("    CAR PRICE INFLATION ANALYSIS - BRANDWISE DATASET")
        print("    Using Car_Dataset_BrandWise.xlsx")
        print("=" * 80)
        print("=" * 80)
        
        # Load and clean data
        self.load_data()
        self.clean_brand_data()
        
        # Calculate inflation
        self.calculate_brand_inflation()
        
        # ML modeling
        X, y = self.prepare_features_for_ml()
        self.train_ml_models(X, y)
        self.find_best_model()
        
        # Summary
        self.print_summary()
        
        print("\n" + "=" * 80)
        print("    ANALYSIS COMPLETE!")
        print("=" * 80 + "\n")


def main():
    # Use the BrandWise dataset
    excel_path = r"C:\Users\Mahina Varma\OneDrive\Desktop\Car_Dataset_BrandWise.xlsx"
    
    analyzer = BrandWiseCarInflationAnalyzer(excel_path)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
