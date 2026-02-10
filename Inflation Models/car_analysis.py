"""
Car Price Inflation Analysis
Analyzes car price trends and calculates depreciation/inflation rates
Tests multiple ML algorithms to find the best one
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class CarInflationAnalyzer:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.car_data = None
        self.models = {}
        self.results = {}
        self.label_encoders = {}
        
    def load_data(self):
        """Load car data from Excel"""
        print("\n" + "=" * 70)
        print("    LOADING CAR DATA FROM EXCEL")
        print("=" * 70)
        
        self.car_data = pd.read_excel(self.excel_path, sheet_name='Car Data')
        
        print(f"\n  Total Records: {len(self.car_data)}")
        print(f"  Columns: {list(self.car_data.columns)}")
        print(f"\n  Sample Data:")
        print(self.car_data.head())
        
        # Basic stats
        print(f"\n  Year Range: {self.car_data['year'].min()} - {self.car_data['year'].max()}")
        print(f"  Price Range: Rs. {self.car_data['selling_price'].min():,} - Rs. {self.car_data['selling_price'].max():,}")
        
    def calculate_yearly_prices(self):
        """Calculate average car prices by year"""
        print("\n" + "=" * 70)
        print("    CAR PRICES BY YEAR (MANUFACTURING YEAR)")
        print("=" * 70)
        
        df = self.car_data.copy()
        
        # Group by year
        yearly = df.groupby('year').agg({
            'selling_price': ['mean', 'median', 'min', 'max', 'count']
        }).reset_index()
        yearly.columns = ['Year', 'Avg_Price', 'Median_Price', 'Min_Price', 'Max_Price', 'Count']
        
        # Calculate year-over-year change
        yearly['YoY_Change'] = yearly['Avg_Price'].pct_change() * 100
        
        print(f"\n  {'Year':<8} {'Avg Price':>12} {'Count':>8} {'YoY Change':>12}")
        print("  " + "-" * 45)
        
        for _, row in yearly.iterrows():
            yoy = row['YoY_Change']
            yoy_str = f"{yoy:+.2f}%" if pd.notna(yoy) else "N/A"
            print(f"  {int(row['Year']):<8} Rs.{row['Avg_Price']:>9,.0f} {int(row['Count']):>8} {yoy_str:>12}")
        
        print("  " + "-" * 45)
        
        self.yearly_data = yearly
        return yearly
    
    def calculate_depreciation(self):
        """Calculate car depreciation rate (opposite of inflation)"""
        print("\n" + "=" * 70)
        print("    CAR DEPRECIATION/INFLATION ANALYSIS")
        print("=" * 70)
        
        df = self.car_data.copy()
        
        # Cars depreciate with age, not appreciate
        # But new car prices (by manufacturing year) show inflation
        
        yearly = self.yearly_data
        
        # Get first and last year data
        first_year = yearly['Year'].min()
        last_year = yearly['Year'].max()
        first_price = yearly[yearly['Year'] == first_year]['Avg_Price'].values[0]
        last_price = yearly[yearly['Year'] == last_year]['Avg_Price'].values[0]
        
        total_years = last_year - first_year
        
        # Total change
        total_change = ((last_price - first_price) / first_price) * 100
        
        # CAGR
        if total_years > 0:
            cagr = ((last_price / first_price) ** (1 / total_years) - 1) * 100
        else:
            cagr = 0
        
        # Average YoY
        avg_yoy = yearly['YoY_Change'].dropna().mean()
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"\n  Avg Price ({first_year}): Rs. {first_price:,.0f}")
        print(f"  Avg Price ({last_year}): Rs. {last_price:,.0f}")
        
        print(f"\n  " + "-" * 50)
        print(f"  PRICE CHANGE ANALYSIS:")
        print(f"  " + "-" * 50)
        print(f"  Total Price Change:        {total_change:>10.2f}%")
        print(f"  CAGR (Annual Rate):        {cagr:>10.2f}%")
        print(f"  Average YoY Change:        {avg_yoy:>10.2f}%")
        print(f"  " + "-" * 50)
        
        if cagr > 0:
            print(f"\n  >>> CAR PRICE INFLATION: {cagr:.2f}% per year")
        else:
            print(f"\n  >>> CAR PRICE DEPRECIATION: {abs(cagr):.2f}% per year")
        
        return {
            'total_change': total_change,
            'cagr': cagr,
            'avg_yoy': avg_yoy,
            'first_price': first_price,
            'last_price': last_price
        }
    
    def prepare_features(self):
        """Prepare features for ML models"""
        print("\n" + "=" * 70)
        print("    PREPARING FEATURES FOR ML MODELS")
        print("=" * 70)
        
        df = self.car_data.copy()
        
        # Encode categorical variables
        categorical_cols = ['fuel', 'seller_type', 'transmission', 'owner']
        
        for col in categorical_cols:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le
        
        # Create features
        df['car_age'] = 2026 - df['year']  # Age of car
        df['km_per_year'] = df['km_driven'] / (df['car_age'] + 1)  # Avoid division by zero
        
        # Feature columns
        feature_cols = ['year', 'km_driven', 'fuel_encoded', 'seller_type_encoded', 
                       'transmission_encoded', 'owner_encoded', 'car_age', 'km_per_year']
        
        X = df[feature_cols]
        y = df['selling_price']
        
        print(f"\n  Features: {feature_cols}")
        print(f"  Total samples: {len(X)}")
        print(f"  Target: selling_price")
        
        return X, y
    
    def train_all_models(self, X, y):
        """Train multiple ML models and compare"""
        print("\n" + "=" * 70)
        print("    TRAINING MULTIPLE ML MODELS")
        print("=" * 70)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features for some models
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Define models
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=100),
            'Decision Tree': DecisionTreeRegressor(max_depth=10, random_state=42),
            'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
            'KNN': KNeighborsRegressor(n_neighbors=5),
            'SVR': SVR(kernel='rbf', C=100000)
        }
        
        print(f"\n  Training {len(models)} models...")
        print(f"  Train size: {len(X_train)}, Test size: {len(X_test)}")
        
        print(f"\n  +{'-'*25}+{'-'*12}+{'-'*15}+{'-'*15}+")
        print(f"  | {'Model':<23} | {'R² Score':>10} | {'RMSE':>13} | {'MAE':>13} |")
        print(f"  +{'-'*25}+{'-'*12}+{'-'*15}+{'-'*15}+")
        
        for name, model in models.items():
            try:
                # Use scaled data for KNN and SVR
                if name in ['KNN', 'SVR']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                
                # Calculate metrics
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = mean_absolute_error(y_test, y_pred)
                
                self.results[name] = {
                    'r2_score': r2,
                    'rmse': rmse,
                    'mae': mae,
                    'model': model
                }
                
                print(f"  | {name:<23} | {r2*100:>9.2f}% | Rs.{rmse:>9,.0f} | Rs.{mae:>9,.0f} |")
                
            except Exception as e:
                print(f"  | {name:<23} | Error: {str(e)[:20]} |")
        
        print(f"  +{'-'*25}+{'-'*12}+{'-'*15}+{'-'*15}+")
        
        return X_test, y_test
    
    def find_best_model(self):
        """Find and display the best performing model"""
        print("\n" + "=" * 70)
        print("    BEST MODEL ANALYSIS")
        print("=" * 70)
        
        # Sort by R² score
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['r2_score'], reverse=True)
        
        print(f"\n  RANKING BY ACCURACY (R² Score):")
        print(f"\n  +{'-'*6}+{'-'*25}+{'-'*12}+{'-'*15}+")
        print(f"  | {'Rank':^4} | {'Model':<23} | {'R² Score':>10} | {'RMSE':>13} |")
        print(f"  +{'-'*6}+{'-'*25}+{'-'*12}+{'-'*15}+")
        
        for i, (name, metrics) in enumerate(sorted_results, 1):
            marker = "**" if i == 1 else "  "
            print(f"  |{marker}{i:^4}| {name:<23} | {metrics['r2_score']*100:>9.2f}% | Rs.{metrics['rmse']:>9,.0f} |")
        
        print(f"  +{'-'*6}+{'-'*25}+{'-'*12}+{'-'*15}+")
        
        # Best model
        best_name, best_metrics = sorted_results[0]
        
        print(f"\n  {'='*50}")
        print(f"  BEST MODEL: {best_name}")
        print(f"  {'='*50}")
        print(f"  R² Score:  {best_metrics['r2_score']:.4f} ({best_metrics['r2_score']*100:.2f}%)")
        print(f"  RMSE:      Rs. {best_metrics['rmse']:,.0f}")
        print(f"  MAE:       Rs. {best_metrics['mae']:,.0f}")
        
        return best_name, best_metrics
    
    def analyze_feature_importance(self):
        """Analyze which features are most important"""
        print("\n" + "=" * 70)
        print("    FEATURE IMPORTANCE (Random Forest)")
        print("=" * 70)
        
        if 'Random Forest' in self.results:
            rf_model = self.results['Random Forest']['model']
            feature_cols = ['year', 'km_driven', 'fuel_encoded', 'seller_type_encoded', 
                           'transmission_encoded', 'owner_encoded', 'car_age', 'km_per_year']
            
            importance = pd.DataFrame({
                'Feature': feature_cols,
                'Importance': rf_model.feature_importances_
            }).sort_values('Importance', ascending=False)
            
            print(f"\n  {'Feature':<25} {'Importance':>15}")
            print("  " + "-" * 42)
            
            for _, row in importance.iterrows():
                bar = "█" * int(row['Importance'] * 50)
                print(f"  {row['Feature']:<25} {row['Importance']:>8.4f}  {bar}")
    
    def print_summary(self, inflation_data, best_model):
        """Print final summary"""
        print("\n" + "=" * 70)
        print("    FINAL SUMMARY - CAR PRICE ANALYSIS")
        print("=" * 70)
        
        print(f"\n  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Metric':<43} | {'Value':^16} |")
        print(f"  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Total Records Analyzed':<43} | {len(self.car_data):>16,} |")
        print(f"  | {'Year Range':<43} | {self.car_data['year'].min()}-{self.car_data['year'].max():>11} |")
        print(f"  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Total Price Change':<43} | {inflation_data['total_change']:>14.2f}% |")
        print(f"  | {'CAGR (Annual Inflation/Depreciation)':<43} | {inflation_data['cagr']:>14.2f}% |")
        print(f"  | {'Average YoY Change':<43} | {inflation_data['avg_yoy']:>14.2f}% |")
        print(f"  +{'-'*45}+{'-'*18}+")
        print(f"  | {'Best ML Model':<43} | {best_model[0]:>16} |")
        print(f"  | {'Model Accuracy (R²)':<43} | {best_model[1]['r2_score']*100:>14.2f}% |")
        print(f"  | {'Model RMSE':<43} | Rs.{best_model[1]['rmse']:>12,.0f} |")
        print(f"  +{'-'*45}+{'-'*18}+")
        
        if inflation_data['cagr'] > 0:
            print(f"\n  >>> CAR PRICE INFLATION RATE: {inflation_data['cagr']:.2f}% per year")
        else:
            print(f"\n  >>> CAR PRICE TREND: {inflation_data['cagr']:.2f}% per year")
    
    def run_analysis(self):
        """Run complete analysis"""
        print("\n" + "=" * 70)
        print("=" * 70)
        print("    CAR PRICE INFLATION ANALYSIS")
        print("    Testing Multiple ML Algorithms")
        print("=" * 70)
        print("=" * 70)
        
        # Load data
        self.load_data()
        
        # Calculate yearly prices
        self.calculate_yearly_prices()
        
        # Calculate depreciation/inflation
        inflation_data = self.calculate_depreciation()
        
        # Prepare features
        X, y = self.prepare_features()
        
        # Train all models
        self.train_all_models(X, y)
        
        # Find best model
        best_model = self.find_best_model()
        
        # Feature importance
        self.analyze_feature_importance()
        
        # Print summary
        self.print_summary(inflation_data, best_model)
        
        print("\n" + "=" * 70)
        print("    ANALYSIS COMPLETE!")
        print("=" * 70)


def main():
    excel_path = r"c:\Users\Mahina Varma\OneDrive\Desktop\BE Project Datasets\BE Project Implementation\money_mentor\src\combined_dataset_20251005_175959.xlsx"
    
    analyzer = CarInflationAnalyzer(excel_path)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
