"""
Real Estate Price Inflation Analysis - IMPROVED VERSION
Predicts Price per SQFT (market value indicator) from property features
Without data leakage - does NOT use price-derived features to predict price

Key Improvements:
1. Proper target: Predicts Price_per_SQFT (market value) not total price
2. No data leakage: Features don't include price-derived values
3. Feature extraction from text (BHK, Property Type, City, Locality tier)
4. Outlier removal using IQR
5. Log transformation for skewed distributions
6. Hyperparameter-tuned models
7. Cross-validation for robust results
"""

import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, AdaBoostRegressor, ExtraTreesRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')


class ImprovedRealEstateAnalyzer:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.raw_data = None
        self.clean_data = None
        self.models = {}
        self.results = {}
        self.label_encoders = {}
        self.features_used = []
        
    def load_data(self):
        """Load real estate data from Excel"""
        print("\n" + "=" * 70)
        print("    LOADING REAL ESTATE DATA")
        print("=" * 70)
        
        self.raw_data = pd.read_excel(self.excel_path, sheet_name='Real_Estate_Data')
        
        print(f"\n  Original Records: {len(self.raw_data)}")
        print(f"  Columns: {list(self.raw_data.columns)}")
        
    def parse_price(self, price_str):
        """Parse price from string format"""
        if pd.isna(price_str):
            return np.nan
        price_str = str(price_str).lower().replace(',', '').replace(' ', '')
        price_str = price_str.replace('₹', '').replace('rs', '').replace('rs.', '')
        
        if 'cr' in price_str:
            try:
                num = float(re.findall(r'[\d.]+', price_str)[0])
                return num * 10000000
            except:
                return np.nan
        elif 'l' in price_str:
            try:
                num = float(re.findall(r'[\d.]+', price_str)[0])
                return num * 100000
            except:
                return np.nan
        else:
            try:
                return float(re.findall(r'[\d.]+', price_str)[0])
            except:
                return np.nan
    
    def extract_bhk(self, title):
        """Extract BHK from property title"""
        if pd.isna(title):
            return np.nan
        title = str(title).upper()
        match = re.search(r'(\d+)\s*(BHK|RK)', title)
        if match:
            return int(match.group(1))
        return np.nan
    
    def extract_property_type(self, title):
        """Extract property type from title"""
        if pd.isna(title):
            return 'Unknown'
        title = str(title).lower()
        if 'flat' in title or 'apartment' in title:
            return 'Flat'
        elif 'independent house' in title or 'villa' in title:
            return 'House'
        elif 'plot' in title or 'land' in title:
            return 'Plot'
        elif 'penthouse' in title:
            return 'Penthouse'
        else:
            return 'Other'
    
    def extract_city(self, location):
        """Extract city from location"""
        if pd.isna(location):
            return 'Other'
        location = str(location)
        cities = ['Bangalore', 'Mumbai', 'Delhi', 'Pune', 'Chennai', 
                  'Hyderabad', 'Kolkata', 'Gurgaon', 'Noida', 'Thane']
        for city in cities:
            if city.lower() in location.lower():
                return city
        return 'Other'
    
    def extract_locality_tier(self, location):
        """Extract locality tier based on premium areas"""
        if pd.isna(location):
            return 'Standard'
        location = str(location).lower()
        
        # Premium localities (higher prices)
        premium = ['bandra', 'juhu', 'andheri', 'powai', 'worli', 'marine', 
                   'koramangala', 'indiranagar', 'whitefield', 'electronic city',
                   'dwarka', 'defence colony', 'vasant', 'greater kailash',
                   'banjara hills', 'jubilee hills', 'hitech city',
                   'anna nagar', 'adyar', 't nagar', 'velachery',
                   'kothrud', 'viman nagar', 'kalyani nagar', 'hinjewadi']
        
        for area in premium:
            if area in location:
                return 'Premium'
        
        # Developing localities
        developing = ['wagholi', 'hadapsar', 'chakan', 'mira road', 'virar',
                      'yelahanka', 'sarjapur', 'electronic city', 'horamavu',
                      'sector', 'greater noida', 'ghaziabad']
        
        for area in developing:
            if area in location:
                return 'Developing'
        
        return 'Standard'
    
    def extract_floor(self, desc):
        """Extract floor number from description"""
        if pd.isna(desc):
            return -1
        desc = str(desc).lower()
        # Look for floor patterns
        match = re.search(r'(\d+)(?:st|nd|rd|th)?\s*floor', desc)
        if match:
            return min(int(match.group(1)), 50)  # Cap at 50
        if 'ground floor' in desc:
            return 0
        if 'top floor' in desc or 'penthouse' in desc:
            return 20  # Assume high floor
        return -1
    
    def extract_amenities_score(self, desc):
        """Calculate amenities score from description"""
        if pd.isna(desc):
            return 0
        desc = str(desc).lower()
        score = 0
        amenities = ['gym', 'pool', 'swimming', 'garden', 'parking', 'lift', 
                     'security', 'club', 'playground', 'power backup', '24x7',
                     'gated', 'community', 'modular kitchen', 'balcony']
        for amenity in amenities:
            if amenity in desc:
                score += 1
        return score
    
    def extract_new_property(self, desc):
        """Check if property is new or under construction"""
        if pd.isna(desc):
            return 0
        desc = str(desc).lower()
        if any(x in desc for x in ['new', 'newly', 'brand new', 'under construction', 'ready to move']):
            return 1
        if any(x in desc for x in ['resale', 'old', 'years old']):
            return -1
        return 0
        
    def perform_eda(self):
        """Perform Exploratory Data Analysis"""
        print("\n" + "=" * 70)
        print("    EXPLORATORY DATA ANALYSIS")
        print("=" * 70)
        
        df = self.raw_data.copy()
        df['price'] = df['Price'].apply(self.parse_price)
        
        print(f"\n  [PRICE ANALYSIS]")
        print(f"  Mean Price:      Rs. {df['price'].mean():,.0f}")
        print(f"  Median Price:    Rs. {df['price'].median():,.0f}")
        print(f"  Skewness:        {df['price'].skew():.2f}")
        
        print(f"\n  [PRICE PER SQFT - TARGET VARIABLE]")
        print(f"  Mean:            Rs. {df['Price_per_SQFT'].mean():,.0f}")
        print(f"  Median:          Rs. {df['Price_per_SQFT'].median():,.0f}")
        print(f"  Skewness:        {df['Price_per_SQFT'].skew():.2f}")
        
        print(f"\n  [TOTAL AREA ANALYSIS]")
        print(f"  Mean Area:       {df['Total_Area'].mean():,.0f} sq.ft")
        print(f"  Median Area:     {df['Total_Area'].median():,.0f} sq.ft")
        
        # Outlier counts
        print(f"\n  [OUTLIERS DETECTED]")
        for col in ['Price_per_SQFT', 'Total_Area']:
            Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
            print(f"  {col}: {len(outliers)} ({len(outliers)/len(df)*100:.1f}%)")
            
        print(f"\n  [KEY INSIGHT]")
        print(f"  Target: Price_per_SQFT (market value indicator)")
        print(f"  This represents the real estate price per square foot")
        print(f"  Higher values = more expensive/premium areas")
        
    def clean_data_eda_based(self):
        """Clean data based on EDA findings"""
        print("\n" + "=" * 70)
        print("    DATA CLEANING (EDA-BASED)")
        print("=" * 70)
        
        df = self.raw_data.copy()
        original_count = len(df)
        
        # 1. Parse price
        df['price'] = df['Price'].apply(self.parse_price)
        print(f"\n  [1] Parsed price from text format")
        
        # 2. Extract features from text
        df['BHK'] = df['Property Title'].apply(self.extract_bhk)
        df['Property_Type'] = df['Property Title'].apply(self.extract_property_type)
        df['City'] = df['Location'].apply(self.extract_city)
        df['Locality_Tier'] = df['Location'].apply(self.extract_locality_tier)
        print(f"  [2] Extracted BHK, Property_Type, City, Locality_Tier from text")
        
        # 2b. Extract features from Description
        df['Floor'] = df['Description'].apply(self.extract_floor)
        df['Amenities_Score'] = df['Description'].apply(self.extract_amenities_score)
        df['Is_New'] = df['Description'].apply(self.extract_new_property)
        print(f"  [2b] Extracted Floor, Amenities_Score, Is_New from Description")
        
        # 3. Remove invalid prices
        before = len(df)
        df = df[df['price'].notna() & (df['price'] > 0)]
        print(f"  [3] Removed {before - len(df)} invalid prices")
        
        # 4. Remove missing BHK
        before = len(df)
        df = df[df['BHK'].notna()]
        print(f"  [4] Removed {before - len(df)} missing BHK")
        
        # 5. Remove Price_per_SQFT outliers (target variable)
        Q1, Q3 = df['Price_per_SQFT'].quantile(0.25), df['Price_per_SQFT'].quantile(0.75)
        IQR = Q3 - Q1
        before = len(df)
        df = df[(df['Price_per_SQFT'] >= Q1 - 1.5*IQR) & (df['Price_per_SQFT'] <= Q3 + 1.5*IQR)]
        print(f"  [5] Removed {before - len(df)} Price_per_SQFT outliers")
        
        # 6. Remove Area outliers
        Q1, Q3 = df['Total_Area'].quantile(0.25), df['Total_Area'].quantile(0.75)
        IQR = Q3 - Q1
        before = len(df)
        df = df[(df['Total_Area'] >= Q1 - 1.5*IQR) & (df['Total_Area'] <= Q3 + 1.5*IQR)]
        print(f"  [6] Removed {before - len(df)} Area outliers")
        
        # 7. Keep reasonable BHK (1-6)
        before = len(df)
        df = df[(df['BHK'] >= 1) & (df['BHK'] <= 6)]
        print(f"  [7] Kept BHK 1-6, removed {before - len(df)} extreme values")
        
        # 8. Remove zero/invalid Price_per_SQFT
        before = len(df)
        df = df[df['Price_per_SQFT'] > 100]  # Minimum realistic price/sqft
        print(f"  [8] Removed {before - len(df)} unrealistic Price_per_SQFT values")
        
        # 9. Log transformations
        df['log_price_sqft'] = np.log1p(df['Price_per_SQFT'])
        df['log_area'] = np.log1p(df['Total_Area'])
        print(f"  [9] Applied log transformation")
        
        print(f"\n  Final dataset: {len(df)} records ({len(df)/original_count*100:.1f}% retained)")
        
        self.clean_data = df
        
    def engineer_features(self):
        """Create advanced features WITHOUT data leakage"""
        print("\n" + "=" * 70)
        print("    FEATURE ENGINEERING (NO DATA LEAKAGE)")
        print("=" * 70)
        
        df = self.clean_data.copy()
        
        # Encode categorical variables
        categorical_cols = ['Property_Type', 'City', 'Balcony', 'Locality_Tier']
        
        for col in categorical_cols:
            le = LabelEncoder()
            df[col + '_encoded'] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le
        
        # Create derived features (WITHOUT using price-related data)
        df['area_per_bhk'] = df['Total_Area'] / df['BHK']
        df['log_area_per_bhk'] = np.log1p(df['area_per_bhk'])
        
        # BHK polynomial features
        df['BHK_sq'] = df['BHK'] ** 2
        
        # Baths per BHK ratio
        df['baths_per_bhk'] = df['Baths'] / df['BHK']
        
        # Area polynomial
        df['log_area_sq'] = df['log_area'] ** 2
        
        # Interaction features
        df['bhk_area'] = df['BHK'] * df['log_area']
        df['bhk_baths'] = df['BHK'] * df['Baths']
        
        # City-based interactions
        df['city_bhk'] = df['City_encoded'] * df['BHK']
        df['city_area'] = df['City_encoded'] * df['log_area']
        
        # Amenity interactions
        df['amenity_area'] = df['Amenities_Score'] * df['log_area']
        
        # Floor features
        df['has_floor_info'] = (df['Floor'] >= 0).astype(int)
        df['floor_normalized'] = df['Floor'].apply(lambda x: x if x >= 0 else 5)  # Default floor 5
        
        print(f"\n  Features created (NO PRICE LEAKAGE):")
        print(f"  - Categorical: Property_Type, City, Balcony, Locality_Tier")
        print(f"  - From Description: Floor, Amenities_Score, Is_New")
        print(f"  - Derived: area_per_bhk, BHK_sq, baths_per_bhk")
        print(f"  - Interactions: bhk_area, bhk_baths, city_bhk, city_area, amenity_area")
        
        self.clean_data = df
        
    def train_models(self):
        """Train and compare multiple models"""
        print("\n" + "=" * 70)
        print("    TRAINING ML MODELS")
        print("=" * 70)
        
        df = self.clean_data
        
        # Features WITHOUT price leakage
        # We predict Price_per_SQFT from property characteristics only
        features = ['BHK', 'log_area', 'Baths', 
                   'Property_Type_encoded', 'City_encoded', 'Balcony_encoded',
                   'Locality_Tier_encoded', 'log_area_per_bhk', 'BHK_sq', 
                   'baths_per_bhk', 'log_area_sq', 'bhk_area', 'bhk_baths',
                   'Floor', 'Amenities_Score', 'Is_New', 'city_bhk', 'city_area',
                   'amenity_area', 'has_floor_info', 'floor_normalized']
        
        print(f"\n  Target: log(Price_per_SQFT) - Market Value Indicator")
        print(f"  Using {len(features)} features (NO price leakage):")
        print(f"  {features}")
        
        X = df[features]
        y = df['log_price_sqft']  # Predicting log(Price per SQFT)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Define models with tuned hyperparameters
        models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=10),
            'Lasso Regression': Lasso(alpha=0.01),
            'ElasticNet': ElasticNet(alpha=0.01, l1_ratio=0.5),
            'Decision Tree': DecisionTreeRegressor(max_depth=20, min_samples_split=10, 
                                                    min_samples_leaf=5, random_state=42),
            'Random Forest': RandomForestRegressor(n_estimators=300, max_depth=20, 
                                                   min_samples_split=5, min_samples_leaf=2,
                                                   random_state=42, n_jobs=-1),
            'Extra Trees': ExtraTreesRegressor(n_estimators=300, max_depth=20,
                                               min_samples_split=5, random_state=42, n_jobs=-1),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=300, max_depth=8, 
                                                           learning_rate=0.05, 
                                                           min_samples_split=5,
                                                           subsample=0.8,
                                                           random_state=42),
            'AdaBoost': AdaBoostRegressor(n_estimators=200, learning_rate=0.1, random_state=42),
            'KNN': KNeighborsRegressor(n_neighbors=10, weights='distance', p=2),
            'SVR': SVR(kernel='rbf', C=100, gamma='scale', epsilon=0.1)
        }
        
        print(f"\n  Training {len(models)} models...")
        print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
        
        print(f"\n  +{'-'*25}+{'-'*12}+{'-'*12}+{'-'*15}+")
        print(f"  | {'Model':<23} | {'R2 Score':>10} | {'CV Score':>10} | {'RMSE (log)':>13} |")
        print(f"  +{'-'*25}+{'-'*12}+{'-'*12}+{'-'*15}+")
        
        for name, model in models.items():
            try:
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
                
                # Convert back to actual price per sqft
                y_test_actual = np.expm1(y_test)
                y_pred_actual = np.expm1(y_pred)
                rmse_actual = np.sqrt(mean_squared_error(y_test_actual, y_pred_actual))
                mae_actual = mean_absolute_error(y_test_actual, y_pred_actual)
                
                self.results[name] = {
                    'r2_score': r2,
                    'cv_score': cv_mean,
                    'rmse_log': rmse,
                    'rmse_actual': rmse_actual,
                    'mae_actual': mae_actual,
                    'model': model
                }
                
                print(f"  | {name:<23} | {r2*100:>9.2f}% | {cv_mean*100:>9.2f}% | {rmse:>13.4f} |")
                
            except Exception as e:
                print(f"  | {name:<23} | Error: {str(e)[:30]} |")
        
        print(f"  +{'-'*25}+{'-'*12}+{'-'*12}+{'-'*15}+")
        
        self.features_used = features
        self.scaler = scaler
        return X_test, y_test
        
    def find_best_model(self):
        """Find and display best model"""
        print("\n" + "=" * 70)
        print("    MODEL COMPARISON & BEST MODEL")
        print("=" * 70)
        
        # Sort by R2 score
        sorted_results = sorted(self.results.items(), key=lambda x: x[1]['r2_score'], reverse=True)
        
        print(f"\n  RANKING BY ACCURACY (R2 Score):")
        print(f"\n  +{'-'*6}+{'-'*25}+{'-'*12}+{'-'*12}+{'-'*18}+")
        print(f"  | {'Rank':^4} | {'Model':<23} | {'R2 Score':>10} | {'CV Score':>10} | {'RMSE (Rs/sqft)':>16} |")
        print(f"  +{'-'*6}+{'-'*25}+{'-'*12}+{'-'*12}+{'-'*18}+")
        
        for i, (name, metrics) in enumerate(sorted_results, 1):
            marker = "**" if i == 1 else "  "
            print(f"  |{marker}{i:^4}| {name:<23} | {metrics['r2_score']*100:>9.2f}% | {metrics['cv_score']*100:>9.2f}% | Rs.{metrics['rmse_actual']:>12,.0f} |")
        
        print(f"  +{'-'*6}+{'-'*25}+{'-'*12}+{'-'*12}+{'-'*18}+")
        
        best_name, best_metrics = sorted_results[0]
        
        print(f"\n  {'='*60}")
        print(f"  BEST MODEL: {best_name}")
        print(f"  {'='*60}")
        print(f"  R2 Score:             {best_metrics['r2_score']*100:.2f}%")
        print(f"  Cross-Validation:     {best_metrics['cv_score']*100:.2f}%")
        print(f"  RMSE (Price/SQFT):    Rs. {best_metrics['rmse_actual']:,.0f}")
        print(f"  MAE (Price/SQFT):     Rs. {best_metrics['mae_actual']:,.0f}")
        
        return best_name, best_metrics
    
    def calculate_inflation_metrics(self):
        """Calculate CAGR and inflation metrics for real estate"""
        print("\n" + "=" * 70)
        print("    INFLATION ANALYSIS")
        print("=" * 70)
        
        df = self.clean_data
        
        # Group by city to analyze price trends
        city_data = df.groupby('City')['Price_per_SQFT'].agg(['min', 'max', 'mean', 'median', 'count'])
        city_data = city_data[city_data['count'] >= 10]  # At least 10 records per city
        
        print(f"\n  Real Estate Price per SQFT (₹) Analysis by City:")
        print(f"\n  +{'-'*15}+{'-'*12}+{'-'*12}+{'-'*12}+{'-'*12}+")
        print(f"  | {'City':<13} | {'Min':>10} | {'Max':>10} | {'Mean':>10} | {'Median':>10} |")
        print(f"  +{'-'*15}+{'-'*12}+{'-'*12}+{'-'*12}+{'-'*12}+")
        
        for city, row in city_data.iterrows():
            print(f"  | {city:<13} | Rs.{row['min']:>8,.0f} | Rs.{row['max']:>8,.0f} | Rs.{row['mean']:>8,.0f} | Rs.{row['median']:>8,.0f} |")
        
        print(f"  +{'-'*15}+{'-'*12}+{'-'*12}+{'-'*12}+{'-'*12}+")
        
        # Overall statistics
        min_price = df['Price_per_SQFT'].min()
        max_price = df['Price_per_SQFT'].max()
        avg_price = df['Price_per_SQFT'].mean()
        
        # Estimate CAGR based on min and max (assuming spread over time)
        # Note: Since this is cross-sectional data, we use min/max as proxy for old/new
        try:
            estimated_years = 10  # Assume 10-year spread
            cagr = ((max_price / min_price) ** (1 / estimated_years) - 1) * 100
        except:
            cagr = 0
        
        print(f"\n  Overall Price per SQFT Statistics:")
        print(f"  Minimum: Rs. {min_price:,.0f}")
        print(f"  Maximum: Rs. {max_price:,.0f}")
        print(f"  Average: Rs. {avg_price:,.0f}")
        print(f"  Total Inflation: {((max_price - min_price) / min_price * 100):.2f}%")
        print(f"  Estimated CAGR (min→max, ~10 years): {cagr:.2f}%")
        
        return {
            'cagr': cagr,
            'avg_price': avg_price,
            'min_price': min_price,
            'max_price': max_price,
            'total_inflation': ((max_price - min_price) / min_price * 100)
        }
    
    def analyze_price_by_city(self):
        """Analyze real estate prices by city"""
        print("\n" + "=" * 70)
        print("    REAL ESTATE PRICE ANALYSIS BY CITY")
        print("=" * 70)
        
        df = self.clean_data
        
        # Price per SQFT by city
        print(f"\n  [PRICE PER SQFT BY CITY]")
        city_stats = df.groupby('City').agg({
            'Price_per_SQFT': ['mean', 'median', 'std'],
            'BHK': 'count'
        }).round(0)
        city_stats.columns = ['Avg_SQFT', 'Median_SQFT', 'Std_SQFT', 'Count']
        city_stats = city_stats.sort_values('Avg_SQFT', ascending=False)
        
        print(f"\n  {'City':<15} {'Avg Rs/SQFT':>12} {'Median':>10} {'Count':>8}")
        print("  " + "-" * 48)
        for city, row in city_stats.iterrows():
            print(f"  {city:<15} Rs.{row['Avg_SQFT']:>8,.0f} Rs.{row['Median_SQFT']:>6,.0f} {int(row['Count']):>8}")
        
        # Price by Property Type
        print(f"\n  [PRICE PER SQFT BY PROPERTY TYPE]")
        type_stats = df.groupby('Property_Type')['Price_per_SQFT'].agg(['mean', 'count']).round(0)
        for ptype, row in type_stats.iterrows():
            print(f"  {ptype:<15} Rs. {row['mean']:>8,.0f} per SQFT ({int(row['count'])} properties)")
        
        # Price by Locality Tier
        print(f"\n  [PRICE PER SQFT BY LOCALITY TIER]")
        tier_stats = df.groupby('Locality_Tier')['Price_per_SQFT'].agg(['mean', 'count']).round(0)
        tier_stats = tier_stats.sort_values('mean', ascending=False)
        for tier, row in tier_stats.iterrows():
            print(f"  {tier:<15} Rs. {row['mean']:>8,.0f} per SQFT ({int(row['count'])} properties)")
        
        # Overall statistics
        overall_avg = df['Price_per_SQFT'].mean()
        overall_median = df['Price_per_SQFT'].median()
        
        print(f"\n  [OVERALL STATISTICS]")
        print(f"  Average Price per SQFT:    Rs. {overall_avg:,.0f}")
        print(f"  Median Price per SQFT:     Rs. {overall_median:,.0f}")
        
        return {'avg_sqft': overall_avg, 'median_sqft': overall_median}
    
    def analyze_feature_importance(self):
        """Analyze feature importance"""
        print("\n" + "=" * 70)
        print("    FEATURE IMPORTANCE")
        print("=" * 70)
        
        # Use the best tree-based model
        best_tree = None
        for name in ['Gradient Boosting', 'Random Forest', 'Extra Trees']:
            if name in self.results:
                best_tree = name
                break
        
        if best_tree:
            model = self.results[best_tree]['model']
            
            importance = pd.DataFrame({
                'Feature': self.features_used,
                'Importance': model.feature_importances_
            }).sort_values('Importance', ascending=False)
            
            print(f"\n  Feature importance from {best_tree}:")
            print(f"\n  {'Feature':<25} {'Importance':>12}")
            print("  " + "-" * 40)
            
            for _, row in importance.iterrows():
                bar = "|" * int(row['Importance'] * 50)
                print(f"  {row['Feature']:<25} {row['Importance']*100:>8.2f}%  {bar}")
    
    def print_summary(self, best_model, price_stats):
        """Print final summary"""
        print("\n" + "=" * 70)
        print("    FINAL SUMMARY")
        print("=" * 70)
        
        print(f"\n  +{'-'*50}+{'-'*22}+")
        print(f"  | {'Metric':<48} | {'Value':^20} |")
        print(f"  +{'-'*50}+{'-'*22}+")
        print(f"  | {'Records Analyzed':<48} | {len(self.clean_data):>20,} |")
        print(f"  | {'Features Used (No Price Leakage)':<48} | {len(self.features_used):>20} |")
        print(f"  | {'Cities Covered':<48} | {self.clean_data['City'].nunique():>20} |")
        print(f"  | {'Property Types':<48} | {self.clean_data['Property_Type'].nunique():>20} |")
        print(f"  +{'-'*50}+{'-'*22}+")
        print(f"  | {'Average Price per SQFT':<48} | Rs.{price_stats['avg_sqft']:>16,.0f} |")
        print(f"  | {'Median Price per SQFT':<48} | Rs.{price_stats['median_sqft']:>16,.0f} |")
        print(f"  +{'-'*50}+{'-'*22}+")
        print(f"  | {'Best ML Model':<48} | {best_model[0]:>20} |")
        print(f"  | {'Model Accuracy (R2)':<48} | {best_model[1]['r2_score']*100:>18.2f}% |")
        print(f"  | {'Cross-Validation Score':<48} | {best_model[1]['cv_score']*100:>18.2f}% |")
        print(f"  | {'RMSE (Price per SQFT)':<48} | Rs.{best_model[1]['rmse_actual']:>16,.0f} |")
        print(f"  +{'-'*50}+{'-'*22}+")
        
        print(f"\n  [KEY INSIGHT]")
        print(f"  The model predicts Price per SQFT (market value indicator)")
        print(f"  with {best_model[1]['r2_score']*100:.2f}% accuracy using only property features")
        print(f"  (BHK, Area, City, Locality, Property Type) - NO price leakage!")
        
    def run_analysis(self):
        """Run complete analysis"""
        print("\n" + "=" * 70)
        print("=" * 70)
        print("    REAL ESTATE PRICE ANALYSIS - IMPROVED VERSION")
        print("    Predicting Price per SQFT (Market Value Indicator)")
        print("    With EDA-Based Improvements & No Data Leakage")
        print("=" * 70)
        print("=" * 70)
        
        # Load data
        self.load_data()
        
        # Perform EDA
        self.perform_eda()
        
        # Clean data
        self.clean_data_eda_based()
        
        # Calculate inflation metrics
        inflation_metrics = self.calculate_inflation_metrics()
        
        # Engineer features
        self.engineer_features()
        
        # Train models
        self.train_models()
        
        # Find best model
        best_model = self.find_best_model()
        
        # Analyze prices by city
        price_stats = self.analyze_price_by_city()
        
        # Feature importance
        self.analyze_feature_importance()
        
        # Print summary
        self.print_summary(best_model, price_stats)
        
        print("\n" + "=" * 70)
        print("    ANALYSIS COMPLETE!")
        print("=" * 70)


def main():
    excel_path = r"c:\Users\Mahina Varma\OneDrive\Desktop\BE Project Datasets\BE Project Implementation\money_mentor\src\combined_dataset_20251005_175959.xlsx"
    
    analyzer = ImprovedRealEstateAnalyzer(excel_path)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
