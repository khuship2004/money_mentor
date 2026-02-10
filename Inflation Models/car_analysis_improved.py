"""
Car Price Inflation Analysis - IMPROVED VERSION
With EDA-based improvements for better accuracy:
1. Brand extraction from car name
2. Outlier removal (IQR method)
3. Log transformation for skewed data
4. Better feature engineering
5. Cross-validation for robust results
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class ImprovedCarAnalyzer:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.raw_data = None
        self.clean_data = None
        self.models = {}
        self.results = {}
        self.label_encoders = {}
        
    def load_data(self):
        """Load car data from Excel"""
        print("\n" + "=" * 70)
        print("    LOADING CAR DATA")
        print("=" * 70)
        
        self.raw_data = pd.read_excel(self.excel_path, sheet_name='Car Data')
        
        print(f"\n  Original Records: {len(self.raw_data)}")
        print(f"  Columns: {list(self.raw_data.columns)}")
        print(f"\n  Price Range: Rs. {self.raw_data['selling_price'].min():,} - Rs. {self.raw_data['selling_price'].max():,}")
        print(f"  Year Range: {self.raw_data['year'].min()} - {self.raw_data['year'].max()}")
        
    def perform_eda(self):
        """Perform Exploratory Data Analysis"""
        print("\n" + "=" * 70)
        print("    EXPLORATORY DATA ANALYSIS")
        print("=" * 70)
        
        df = self.raw_data.copy()
        
        # Price Analysis
        print(f"\n  [PRICE ANALYSIS]")
        print(f"  Mean Price:      Rs. {df['selling_price'].mean():,.0f}")
        print(f"  Median Price:    Rs. {df['selling_price'].median():,.0f}")
        print(f"  Std Deviation:   Rs. {df['selling_price'].std():,.0f}")
        print(f"  Skewness:        {df['selling_price'].skew():.2f} (high = heavily right-skewed)")
        
        # KM Driven Analysis
        print(f"\n  [KM DRIVEN ANALYSIS]")
        print(f"  Mean KM:         {df['km_driven'].mean():,.0f}")
        print(f"  Median KM:       {df['km_driven'].median():,.0f}")
        print(f"  Skewness:        {df['km_driven'].skew():.2f}")
        
        # Outlier Detection
        print(f"\n  [OUTLIERS DETECTED]")
        Q1_price = df['selling_price'].quantile(0.25)
        Q3_price = df['selling_price'].quantile(0.75)
        IQR_price = Q3_price - Q1_price
        price_outliers = df[(df['selling_price'] < Q1_price - 1.5*IQR_price) | 
                           (df['selling_price'] > Q3_price + 1.5*IQR_price)]
        print(f"  Price outliers:  {len(price_outliers)} ({len(price_outliers)/len(df)*100:.1f}%)")
        
        Q1_km = df['km_driven'].quantile(0.25)
        Q3_km = df['km_driven'].quantile(0.75)
        IQR_km = Q3_km - Q1_km
        km_outliers = df[(df['km_driven'] < Q1_km - 1.5*IQR_km) | 
                        (df['km_driven'] > Q3_km + 1.5*IQR_km)]
        print(f"  KM outliers:     {len(km_outliers)} ({len(km_outliers)/len(df)*100:.1f}%)")
        
        # Categorical Distribution
        print(f"\n  [CATEGORICAL DISTRIBUTION]")
        print(f"  Fuel Types:      {df['fuel'].value_counts().to_dict()}")
        print(f"  Transmission:    {df['transmission'].value_counts().to_dict()}")
        
        # Brand Analysis
        df['brand'] = df['name'].str.split().str[0]
        print(f"\n  [BRAND ANALYSIS]")
        print(f"  Unique Brands:   {df['brand'].nunique()}")
        print(f"  Top 5 Brands:    {df['brand'].value_counts().head().to_dict()}")
        
    def clean_data_eda_based(self):
        """Clean data based on EDA findings"""
        print("\n" + "=" * 70)
        print("    DATA CLEANING (EDA-BASED)")
        print("=" * 70)
        
        df = self.raw_data.copy()
        original_count = len(df)
        
        # 1. Extract brand from name
        df['brand'] = df['name'].str.split().str[0]
        print(f"\n  [1] Extracted brand from car name: {df['brand'].nunique()} unique brands")
        
        # 2. Remove price outliers (IQR method)
        Q1_price = df['selling_price'].quantile(0.25)
        Q3_price = df['selling_price'].quantile(0.75)
        IQR_price = Q3_price - Q1_price
        before = len(df)
        df = df[(df['selling_price'] >= Q1_price - 1.5*IQR_price) & 
                (df['selling_price'] <= Q3_price + 1.5*IQR_price)]
        print(f"  [2] Removed {before - len(df)} price outliers")
        
        # 3. Remove km_driven outliers
        Q1_km = df['km_driven'].quantile(0.25)
        Q3_km = df['km_driven'].quantile(0.75)
        IQR_km = Q3_km - Q1_km
        before = len(df)
        df = df[(df['km_driven'] >= Q1_km - 1.5*IQR_km) & 
                (df['km_driven'] <= Q3_km + 1.5*IQR_km)]
        print(f"  [3] Removed {before - len(df)} km_driven outliers")
        
        # 4. Keep only common fuel types (remove rare categories)
        before = len(df)
        df = df[df['fuel'].isin(['Diesel', 'Petrol'])]
        print(f"  [4] Removed {before - len(df)} rare fuel types (Electric, LPG, CNG)")
        
        # 5. Apply log transformation
        df['log_price'] = np.log1p(df['selling_price'])
        df['log_km'] = np.log1p(df['km_driven'])
        print(f"  [5] Applied log transformation to price and km (reduces skewness)")
        
        print(f"\n  Final dataset: {len(df)} records ({len(df)/original_count*100:.1f}% retained)")
        
        self.clean_data = df
        
    def engineer_features(self):
        """Create advanced features based on EDA"""
        print("\n" + "=" * 70)
        print("    FEATURE ENGINEERING")
        print("=" * 70)
        
        df = self.clean_data.copy()
        
        # Encode categorical variables
        categorical_cols = ['fuel', 'seller_type', 'transmission', 'owner', 'brand']
        
        for col in categorical_cols:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le
        
        # Create derived features
        df['car_age'] = 2026 - df['year']
        df['km_per_year'] = df['km_driven'] / (df['car_age'] + 1)
        df['log_km_per_year'] = np.log1p(df['km_per_year'])
        
        # Brand price tier (average price for each brand)
        brand_avg_price = df.groupby('brand')['selling_price'].mean()
        df['brand_avg_price'] = df['brand'].map(brand_avg_price)
        df['log_brand_price'] = np.log1p(df['brand_avg_price'])
        
        # Price per km (value indicator)
        df['price_per_km'] = df['selling_price'] / (df['km_driven'] + 1)
        
        # Age squared (non-linear depreciation)
        df['car_age_sq'] = df['car_age'] ** 2
        
        print(f"\n  Features created:")
        print(f"  - brand (extracted from name)")
        print(f"  - Encoded: fuel, seller_type, transmission, owner, brand")
        print(f"  - Derived: car_age, km_per_year, log_km_per_year")
        print(f"  - Advanced: brand_avg_price, price_per_km, car_age_sq")
        
        self.clean_data = df
        
    def train_models(self):
        """Train and compare multiple models"""
        print("\n" + "=" * 70)
        print("    TRAINING ML MODELS (IMPROVED)")
        print("=" * 70)
        
        df = self.clean_data
        
        # Define feature sets
        features_basic = ['year', 'log_km', 'fuel_encoded', 'transmission_encoded', 
                         'owner_encoded', 'car_age', 'log_km_per_year', 'seller_type_encoded']
        
        features_advanced = features_basic + ['brand_encoded', 'log_brand_price', 'car_age_sq']
        
        print(f"\n  Using ADVANCED feature set ({len(features_advanced)} features):")
        print(f"  {features_advanced}")
        
        X = df[features_advanced]
        y = df['log_price']  # Predicting log(price) for better results
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Define models with tuned hyperparameters
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=0.001),
            'Decision Tree': DecisionTreeRegressor(max_depth=15, min_samples_split=5, random_state=42),
            'Random Forest': RandomForestRegressor(n_estimators=200, max_depth=15, min_samples_split=5, 
                                                   random_state=42, n_jobs=-1),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=200, max_depth=7, 
                                                           learning_rate=0.1, random_state=42),
            'KNN': KNeighborsRegressor(n_neighbors=7, weights='distance'),
            'SVR': SVR(kernel='rbf', C=10, gamma='scale')
        }
        
        print(f"\n  Training {len(models)} models...")
        print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
        print(f"  Target: log(selling_price) for normalized predictions")
        
        print(f"\n  +{'-'*25}+{'-'*12}+{'-'*12}+{'-'*15}+")
        print(f"  | {'Model':<23} | {'R² Score':>10} | {'CV Score':>10} | {'RMSE (log)':>13} |")
        print(f"  +{'-'*25}+{'-'*12}+{'-'*12}+{'-'*15}+")
        
        for name, model in models.items():
            try:
                # Use scaled data for KNN and SVR
                if name in ['KNN', 'SVR']:
                    model.fit(X_train_scaled, y_train)
                    y_pred = model.predict(X_test_scaled)
                    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
                else:
                    model.fit(X_train, y_train)
                    y_pred = model.predict(X_test)
                    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
                
                # Calculate metrics
                r2 = r2_score(y_test, y_pred)
                rmse = np.sqrt(mean_squared_error(y_test, y_pred))
                mae = mean_absolute_error(y_test, y_pred)
                cv_mean = cv_scores.mean()
                
                # Convert predictions back to actual prices for interpretability
                y_test_actual = np.expm1(y_test)
                y_pred_actual = np.expm1(y_pred)
                rmse_actual = np.sqrt(mean_squared_error(y_test_actual, y_pred_actual))
                
                self.results[name] = {
                    'r2_score': r2,
                    'cv_score': cv_mean,
                    'rmse_log': rmse,
                    'rmse_actual': rmse_actual,
                    'mae': mae,
                    'model': model
                }
                
                print(f"  | {name:<23} | {r2*100:>9.2f}% | {cv_mean*100:>9.2f}% | {rmse:>13.4f} |")
                
            except Exception as e:
                print(f"  | {name:<23} | Error: {str(e)[:30]} |")
        
        print(f"  +{'-'*25}+{'-'*12}+{'-'*12}+{'-'*15}+")
        
        self.features_used = features_advanced
        return X_test, y_test
        
    def find_best_model(self):
        """Find and display best model"""
        print("\n" + "=" * 70)
        print("    MODEL COMPARISON & BEST MODEL")
        print("=" * 70)
        
        # Sort by R² score
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['r2_score'], reverse=True)
        
        print(f"\n  RANKING BY ACCURACY:")
        print(f"\n  +{'-'*6}+{'-'*25}+{'-'*12}+{'-'*12}+{'-'*18}+")
        print(f"  | {'Rank':^4} | {'Model':<23} | {'R² Score':>10} | {'CV Score':>10} | {'RMSE (Actual)':>16} |")
        print(f"  +{'-'*6}+{'-'*25}+{'-'*12}+{'-'*12}+{'-'*18}+")
        
        for i, (name, metrics) in enumerate(sorted_results, 1):
            marker = "**" if i == 1 else "  "
            print(f"  |{marker}{i:^4}| {name:<23} | {metrics['r2_score']*100:>9.2f}% | {metrics['cv_score']*100:>9.2f}% | Rs.{metrics['rmse_actual']:>12,.0f} |")
        
        print(f"  +{'-'*6}+{'-'*25}+{'-'*12}+{'-'*12}+{'-'*18}+")
        
        best_name, best_metrics = sorted_results[0]
        
        print(f"\n  {'='*55}")
        print(f"  BEST MODEL: {best_name}")
        print(f"  {'='*55}")
        print(f"  R² Score:         {best_metrics['r2_score']*100:.2f}%")
        print(f"  Cross-Val Score:  {best_metrics['cv_score']*100:.2f}%")
        print(f"  RMSE (Actual):    Rs. {best_metrics['rmse_actual']:,.0f}")
        
        return best_name, best_metrics
    
    def calculate_inflation(self):
        """Calculate car price inflation"""
        print("\n" + "=" * 70)
        print("    CAR PRICE INFLATION ANALYSIS")
        print("=" * 70)
        
        df = self.clean_data
        
        # Group by year
        yearly = df.groupby('year').agg({
            'selling_price': ['mean', 'count']
        }).reset_index()
        yearly.columns = ['Year', 'Avg_Price', 'Count']
        
        first_year = yearly['Year'].min()
        last_year = yearly['Year'].max()
        first_price = yearly[yearly['Year'] == first_year]['Avg_Price'].values[0]
        last_price = yearly[yearly['Year'] == last_year]['Avg_Price'].values[0]
        total_years = last_year - first_year
        
        # CAGR
        cagr = ((last_price / first_price) ** (1 / total_years) - 1) * 100
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"  First Year Avg Price: Rs. {first_price:,.0f}")
        print(f"  Last Year Avg Price:  Rs. {last_price:,.0f}")
        print(f"\n  >>> CAGR (Annual Inflation): {cagr:.2f}%")
        
        return {'cagr': cagr, 'first_price': first_price, 'last_price': last_price}
    
    def analyze_feature_importance(self):
        """Analyze feature importance"""
        print("\n" + "=" * 70)
        print("    FEATURE IMPORTANCE")
        print("=" * 70)
        
        if 'Gradient Boosting' in self.results:
            model = self.results['Gradient Boosting']['model']
            
            importance = pd.DataFrame({
                'Feature': self.features_used,
                'Importance': model.feature_importances_
            }).sort_values('Importance', ascending=False)
            
            print(f"\n  {'Feature':<25} {'Importance':>12}")
            print("  " + "-" * 40)
            
            for _, row in importance.iterrows():
                bar = "█" * int(row['Importance'] * 40)
                print(f"  {row['Feature']:<25} {row['Importance']*100:>8.2f}%  {bar}")
    
    def compare_with_original(self, original_r2=50.52):
        """Compare improved model with original"""
        print("\n" + "=" * 70)
        print("    IMPROVEMENT COMPARISON")
        print("=" * 70)
        
        best_name = max(self.results.items(), key=lambda x: x[1]['r2_score'])
        new_r2 = best_name[1]['r2_score'] * 100
        
        improvement = new_r2 - original_r2
        improvement_pct = (improvement / original_r2) * 100
        
        print(f"\n  Original Gradient Boosting R²: {original_r2:.2f}%")
        print(f"  Improved {best_name[0]} R²:     {new_r2:.2f}%")
        print(f"\n  +{'-'*45}+")
        print(f"  | IMPROVEMENT: +{improvement:.2f}% ({improvement_pct:.1f}% better) |")
        print(f"  +{'-'*45}+")
        
        print(f"\n  Key improvements that helped:")
        print(f"  1. Brand extraction from car name (major factor)")
        print(f"  2. Log transformation on price & km (normalized skewed data)")
        print(f"  3. Outlier removal using IQR method")
        print(f"  4. Brand average price as feature (captures luxury vs economy)")
        print(f"  5. Better hyperparameter tuning")
        
    def run_analysis(self):
        """Run complete improved analysis"""
        print("\n" + "=" * 70)
        print("=" * 70)
        print("    CAR PRICE ANALYSIS - IMPROVED VERSION")
        print("    With EDA-Based Data Cleaning & Feature Engineering")
        print("=" * 70)
        print("=" * 70)
        
        # Load data
        self.load_data()
        
        # Perform EDA
        self.perform_eda()
        
        # Clean data based on EDA
        self.clean_data_eda_based()
        
        # Engineer features
        self.engineer_features()
        
        # Train models
        self.train_models()
        
        # Find best model
        best_model = self.find_best_model()
        
        # Calculate inflation
        inflation = self.calculate_inflation()
        
        # Feature importance
        self.analyze_feature_importance()
        
        # Compare with original
        self.compare_with_original(original_r2=50.52)
        
        # Final summary
        print("\n" + "=" * 70)
        print("    FINAL SUMMARY")
        print("=" * 70)
        print(f"\n  Records Analyzed:     {len(self.clean_data):,}")
        print(f"  Features Used:        {len(self.features_used)}")
        print(f"  Best Model:           {best_model[0]}")
        print(f"  Best R² Score:        {best_model[1]['r2_score']*100:.2f}%")
        print(f"  Annual Inflation:     {inflation['cagr']:.2f}%")
        
        print("\n" + "=" * 70)
        print("    ANALYSIS COMPLETE!")
        print("=" * 70)


def main():
    excel_path = r"c:\Users\Mahina Varma\OneDrive\Desktop\BE Project Implementation\money_mentor\src\combined_dataset_20251005_175959.xlsx"
    
    analyzer = ImprovedCarAnalyzer(excel_path)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
