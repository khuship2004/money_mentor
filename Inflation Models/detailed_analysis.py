"""
Detailed Investment Analysis - Gold, Car & Real Estate
Comprehensive comparison with detailed statistics for all three asset classes
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class DetailedInvestmentAnalyzer:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.results = {}
        
    def analyze_gold_detailed(self):
        """Detailed Gold inflation analysis"""
        print("\n" + "█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "  1. GOLD - DETAILED INFLATION ANALYSIS".ljust(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)
        
        # Load gold data
        gold_data = pd.read_excel(self.excel_path, sheet_name='Gold_Data')
        gold_data['Date'] = pd.to_datetime(gold_data['Date'])
        gold_data['Year'] = gold_data['Date'].dt.year
        gold_data['Month'] = gold_data['Date'].dt.month
        
        # ===== BASIC STATISTICS =====
        print("\n" + "=" * 70)
        print("  A. DATA OVERVIEW")
        print("=" * 70)
        print(f"\n  Data Source:      Excel Dataset (Gold_Data sheet)")
        print(f"  Total Records:    {len(gold_data):,}")
        print(f"  Date Range:       {gold_data['Date'].min().strftime('%Y-%m-%d')} to {gold_data['Date'].max().strftime('%Y-%m-%d')}")
        print(f"  Columns:          {list(gold_data.columns)}")
        
        # ===== DESCRIPTIVE STATISTICS =====
        print("\n" + "=" * 70)
        print("  B. DESCRIPTIVE STATISTICS")
        print("=" * 70)
        
        print(f"\n  Price Statistics (Rs.):")
        print(f"  ┌{'─'*30}┬{'─'*20}┐")
        print(f"  │ {'Statistic':<28} │ {'Value':>18} │")
        print(f"  ├{'─'*30}┼{'─'*20}┤")
        print(f"  │ {'Minimum Price':<28} │ Rs. {gold_data['Price'].min():>13,.0f} │")
        print(f"  │ {'Maximum Price':<28} │ Rs. {gold_data['Price'].max():>13,.0f} │")
        print(f"  │ {'Mean Price':<28} │ Rs. {gold_data['Price'].mean():>13,.0f} │")
        print(f"  │ {'Median Price':<28} │ Rs. {gold_data['Price'].median():>13,.0f} │")
        print(f"  │ {'Standard Deviation':<28} │ Rs. {gold_data['Price'].std():>13,.0f} │")
        print(f"  │ {'Variance':<28} │ {gold_data['Price'].var():>18,.0f} │")
        print(f"  │ {'Skewness':<28} │ {gold_data['Price'].skew():>18.4f} │")
        print(f"  │ {'Kurtosis':<28} │ {gold_data['Price'].kurtosis():>18.4f} │")
        print(f"  └{'─'*30}┴{'─'*20}┘")
        
        # Percentiles
        print(f"\n  Percentile Distribution:")
        percentiles = [10, 25, 50, 75, 90, 95, 99]
        for p in percentiles:
            val = gold_data['Price'].quantile(p/100)
            print(f"    {p}th Percentile: Rs. {val:>12,.0f}")
        
        # ===== YEARLY ANALYSIS =====
        print("\n" + "=" * 70)
        print("  C. YEAR-BY-YEAR ANALYSIS")
        print("=" * 70)
        
        yearly = gold_data.groupby('Year').agg({
            'Price': ['mean', 'min', 'max', 'std', 'count', 'first', 'last']
        }).reset_index()
        yearly.columns = ['Year', 'Avg_Price', 'Min_Price', 'Max_Price', 'Volatility', 'Trading_Days', 'Open', 'Close']
        yearly['YoY_Change'] = yearly['Avg_Price'].pct_change() * 100
        yearly['Range'] = yearly['Max_Price'] - yearly['Min_Price']
        yearly['Range_Pct'] = (yearly['Range'] / yearly['Min_Price']) * 100
        
        print(f"\n  {'Year':<6} {'Avg Price':>12} {'Min':>10} {'Max':>10} {'Range%':>8} {'Volatility':>10} {'Days':>6} {'YoY':>10}")
        print("  " + "-" * 78)
        
        for _, row in yearly.iterrows():
            yoy = f"{row['YoY_Change']:+.2f}%" if pd.notna(row['YoY_Change']) else "N/A"
            print(f"  {int(row['Year']):<6} {row['Avg_Price']:>12,.0f} {row['Min_Price']:>10,.0f} {row['Max_Price']:>10,.0f} {row['Range_Pct']:>7.1f}% {row['Volatility']:>10,.0f} {int(row['Trading_Days']):>6} {yoy:>10}")
        
        print("  " + "-" * 78)
        
        # ===== INFLATION CALCULATIONS =====
        print("\n" + "=" * 70)
        print("  D. INFLATION CALCULATIONS (MULTIPLE METHODS)")
        print("=" * 70)
        
        first_year = yearly['Year'].iloc[0]
        last_year = yearly['Year'].iloc[-1]
        first_price = yearly['Avg_Price'].iloc[0]
        last_price = yearly['Avg_Price'].iloc[-1]
        total_years = last_year - first_year
        
        # Method 1: Total Inflation
        total_inflation = ((last_price - first_price) / first_price) * 100
        
        # Method 2: CAGR
        cagr = ((last_price / first_price) ** (1 / total_years) - 1) * 100
        
        # Method 3: Average YoY
        avg_yoy = yearly['YoY_Change'].dropna().mean()
        
        # Method 4: Geometric Mean
        growth_rates = (yearly['Avg_Price'] / yearly['Avg_Price'].shift(1)).dropna()
        geometric_mean = (np.prod(growth_rates) ** (1 / len(growth_rates)) - 1) * 100
        
        # Method 5: Linear Regression Trend
        X = yearly['Year'].values.reshape(-1, 1)
        y = yearly['Avg_Price'].values
        slope = np.polyfit(yearly['Year'], yearly['Avg_Price'], 1)[0]
        trend_inflation = (slope / yearly['Avg_Price'].mean()) * 100
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"\n  Starting Price (Avg {first_year}):  Rs. {first_price:>12,.2f}")
        print(f"  Ending Price (Avg {last_year}):    Rs. {last_price:>12,.2f}")
        print(f"  Absolute Change:                  Rs. {last_price - first_price:>12,.2f}")
        
        print(f"\n  ┌{'─'*45}┬{'─'*18}┐")
        print(f"  │ {'Method':<43} │ {'Result':>16} │")
        print(f"  ├{'─'*45}┼{'─'*18}┤")
        print(f"  │ {'1. Total Inflation (End-Start)/Start':<43} │ {total_inflation:>15.2f}% │")
        print(f"  │ {'2. CAGR (Compound Annual Growth Rate)':<43} │ {cagr:>15.2f}% │")
        print(f"  │ {'3. Average Year-over-Year Change':<43} │ {avg_yoy:>15.2f}% │")
        print(f"  │ {'4. Geometric Mean of Growth Rates':<43} │ {geometric_mean:>15.2f}% │")
        print(f"  │ {'5. Linear Trend-based Inflation':<43} │ {trend_inflation:>15.2f}% │")
        print(f"  └{'─'*45}┴{'─'*18}┘")
        
        # ===== BEST & WORST YEARS =====
        print("\n" + "=" * 70)
        print("  E. BEST & WORST PERFORMING YEARS")
        print("=" * 70)
        
        valid_years = yearly[yearly['YoY_Change'].notna()].copy()
        best_year = valid_years.loc[valid_years['YoY_Change'].idxmax()]
        worst_year = valid_years.loc[valid_years['YoY_Change'].idxmin()]
        
        print(f"\n  🏆 Best Year:  {int(best_year['Year'])} with {best_year['YoY_Change']:+.2f}% growth")
        print(f"     Price moved from Rs. {best_year['Open']:,.0f} to Rs. {best_year['Close']:,.0f}")
        
        print(f"\n  📉 Worst Year: {int(worst_year['Year'])} with {worst_year['YoY_Change']:+.2f}% change")
        print(f"     Price moved from Rs. {worst_year['Open']:,.0f} to Rs. {worst_year['Close']:,.0f}")
        
        # Most volatile year
        most_volatile = yearly.loc[yearly['Volatility'].idxmax()]
        print(f"\n  📊 Most Volatile: {int(most_volatile['Year'])} (Std Dev: Rs. {most_volatile['Volatility']:,.0f})")
        print(f"     Range: Rs. {most_volatile['Min_Price']:,.0f} - Rs. {most_volatile['Max_Price']:,.0f} ({most_volatile['Range_Pct']:.1f}%)")
        
        # ===== FUTURE PROJECTIONS =====
        print("\n" + "=" * 70)
        print("  F. FUTURE PRICE PROJECTIONS (Using CAGR)")
        print("=" * 70)
        
        current_price = last_price
        print(f"\n  Current Avg Price ({last_year}): Rs. {current_price:,.0f}")
        print(f"  Projected CAGR: {cagr:.2f}%")
        
        print(f"\n  {'Year':<8} {'Projected Price':>18} {'Growth from {}'.format(last_year):>20}")
        print("  " + "-" * 50)
        
        for i in range(1, 11):
            future_year = last_year + i
            projected_price = current_price * ((1 + cagr/100) ** i)
            growth = ((projected_price - current_price) / current_price) * 100
            print(f"  {future_year:<8} Rs. {projected_price:>14,.0f} {growth:>19.2f}%")
        
        print("  " + "-" * 50)
        
        print(f"\n  >>> GOLD ANNUAL INFLATION RATE: {cagr:.2f}% (CAGR)")
        
        self.results['Gold'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'start_price': first_price,
            'end_price': last_price,
            'total_inflation': total_inflation,
            'cagr': cagr,
            'avg_yoy': avg_yoy,
            'geometric_mean': geometric_mean,
            'trend_inflation': trend_inflation,
            'best_year': int(best_year['Year']),
            'best_year_return': best_year['YoY_Change'],
            'worst_year': int(worst_year['Year']),
            'worst_year_return': worst_year['YoY_Change'],
            'volatility': gold_data['Price'].std(),
            'total_records': len(gold_data)
        }
        
    def analyze_car_detailed(self):
        """Detailed Car price inflation analysis based on BrandWise dataset"""
        print("\n" + "█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "  2. CAR - DETAILED PRICE INFLATION ANALYSIS".ljust(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)
        
        import os
        import pandas as pd
        import numpy as np
        car_file = os.path.join(os.path.dirname(__file__), 'Car_Dataset_BrandWise.xlsx')
        if not os.path.exists(car_file):
            car_file = os.path.join(os.path.dirname(self.excel_path), 'Car_Dataset_BrandWise.xlsx')
            
        try:
            car_data = pd.read_excel(car_file, sheet_name='All_Model_Prices', header=3)
            years = [str(y) for y in range(2015, 2026)]
        except Exception as e:
            print(f"\n  Error loading car dataset: {e}")
            return
            
        print("\n" + "=" * 70)
        print("  A. DATA OVERVIEW")
        print("=" * 70)
        print(f"\n  Data Source:      Car_Dataset_BrandWise.xlsx (All_Model_Prices)")
        print(f"  Total Models:     {len(car_data):,}")
        print(f"  Total Brands:     {car_data['Brand'].nunique()}")
        print(f"  Year Range:       2015 - 2025")
        
        print("\n" + "=" * 70)
        print("  B. BRAND-WISE ANALYSIS")
        print("=" * 70)
        
        bvars = car_data.groupby('Brand')[years[-1]].agg(['mean', 'count']).sort_values('mean', ascending=False).dropna()
        for brand, row in bvars.iterrows():
            bar = "█" * min(int(row['mean'] / 5), 30)
            print(f"    {brand:<18} ₹ {row['mean']:>6.2f} L ({int(row['count']):>3} models) {bar}")
        
        print("\n" + "=" * 70)
        print("  C. CATEGORY-WISE ANALYSIS")
        print("=" * 70)
        
        svars = car_data.groupby('Segment')[years[-1]].agg(['mean', 'count']).sort_values('mean', ascending=False).dropna()
        for segment, row in svars.iterrows():
            bar = "█" * min(int(row['mean'] / 5), 30)
            print(f"    {segment:<18} ₹ {row['mean']:>6.2f} L ({int(row['count']):>3} models) {bar}")
            
        print("\n" + "=" * 70)
        print("  D. YEAR-BY-YEAR ANALYSIS")
        print("=" * 70)
        
        yearly_avg = car_data[years].mean()
        yearly = pd.DataFrame({
            'Year': [int(y) for y in years],
            'Avg_Price': yearly_avg.values * 100000
        })
        yearly['YoY_Change'] = yearly['Avg_Price'].pct_change() * 100
        
        print(f"\n  {'Year':<6} {'Avg Base Price':>15} {'YoY Change':>15}")
        print("  " + "-" * 45)
        
        for _, row in yearly.iterrows():
            yoy = f"{row['YoY_Change']:+.2f}%" if pd.notna(row['YoY_Change']) else "N/A"
            print(f"  {int(row['Year']):<6} Rs. {row['Avg_Price']:>10,.0f} {yoy:>15}")
            
        print("  " + "-" * 45)
        
        print("\n" + "=" * 70)
        print("  E. INFLATION CALCULATIONS")
        print("=" * 70)
        
        first_year = yearly['Year'].iloc[0]
        last_year = yearly['Year'].iloc[-1]
        first_price = yearly['Avg_Price'].iloc[0]
        last_price = yearly['Avg_Price'].iloc[-1]
        total_years = last_year - first_year
        
        total_inflation = ((last_price - first_price) / first_price) * 100
        cagr = ((last_price / first_price) ** (1 / total_years) - 1) * 100
        avg_yoy = yearly['YoY_Change'].dropna().mean()
        
        growth_rates = (yearly['Avg_Price'] / yearly['Avg_Price'].shift(1)).dropna()
        geometric_mean = (np.prod(growth_rates) ** (1 / len(growth_rates)) - 1) * 100
        
        slope = np.polyfit(yearly['Year'], yearly['Avg_Price'], 1)[0]
        trend_inflation = (slope / yearly['Avg_Price'].mean()) * 100
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"\n  Starting Avg Price ({first_year}):  Rs. {first_price:>12,.2f}")
        print(f"  Ending Avg Price ({last_year}):    Rs. {last_price:>12,.2f}")
        
        print(f"\n  ┌{'─'*45}┬{'─'*18}┐")
        print(f"  │ {'Method':<43} │ {'Result':>16} │")
        print(f"  ├{'─'*45}┼{'─'*18}┤")
        print(f"  │ {'1. Total Inflation':<43} │ {total_inflation:>15.2f}% │")
        print(f"  │ {'2. CAGR':<43} │ {cagr:>15.2f}% │")
        print(f"  │ {'3. Average YoY':<43} │ {avg_yoy:>15.2f}% │")
        print(f"  │ {'4. Geometric Mean':<43} │ {geometric_mean:>15.2f}% │")
        print(f"  │ {'5. Linear Trend':<43} │ {trend_inflation:>15.2f}% │")
        print(f"  └{'─'*45}┴{'─'*18}┘")
        
        valid_years = yearly[yearly['YoY_Change'].notna()]
        best_year = valid_years.loc[valid_years['YoY_Change'].idxmax()]
        worst_year = valid_years.loc[valid_years['YoY_Change'].idxmin()]
        
        print(f"\n  >>> CAR ANNUAL INFLATION RATE: {cagr:.2f}% (CAGR)\n")
        
        self.results['Car'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'start_price': first_price,
            'end_price': last_price,
            'total_inflation': total_inflation,
            'cagr': cagr,
            'avg_yoy': avg_yoy,
            'geometric_mean': geometric_mean,
            'trend_inflation': trend_inflation,
            'best_year': int(best_year['Year']),
            'best_year_return': best_year['YoY_Change'],
            'worst_year': int(worst_year['Year']),
            'worst_year_return': worst_year['YoY_Change'],
            'total_records': len(car_data)
        }

    def analyze_real_estate_detailed(self):
        """Detailed Real Estate inflation analysis"""
        print("\n" + "█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "  3. REAL ESTATE - DETAILED INFLATION ANALYSIS".ljust(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)
        
        # RBI/NHB Housing Price Index Data
        hpi_all_india = {
            'Year': [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'HPI_Index': [100, 111, 126, 143, 158, 167, 175, 183, 191, 198, 195, 203, 218, 237, 261, 287]
        }
        
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
        
        yearly = pd.DataFrame(hpi_all_india)
        city_df = pd.DataFrame(city_hpi)
        
        # ===== BASIC STATISTICS =====
        print("\n" + "=" * 70)
        print("  A. DATA OVERVIEW")
        print("=" * 70)
        print(f"\n  Data Source:      RBI/NHB Housing Price Index (RESIDEX)")
        print(f"  Base Year:        2010 = 100")
        print(f"  Period:           {yearly['Year'].min()} - {yearly['Year'].max()}")
        print(f"  Total Years:      {len(yearly)}")
        print(f"  Cities Covered:   {len(city_df.columns) - 1}")
        
        # ===== ALL INDIA HPI =====
        print("\n" + "=" * 70)
        print("  B. ALL INDIA HOUSING PRICE INDEX")
        print("=" * 70)
        
        yearly['YoY_Change'] = yearly['HPI_Index'].pct_change() * 100
        yearly['Cumulative_Growth'] = ((yearly['HPI_Index'] / 100) - 1) * 100
        
        print(f"\n  {'Year':<6} {'HPI Index':>12} {'YoY Change':>14} {'Cumulative':>14}")
        print("  " + "-" * 50)
        
        for _, row in yearly.iterrows():
            yoy = f"{row['YoY_Change']:+.2f}%" if pd.notna(row['YoY_Change']) else "N/A"
            print(f"  {int(row['Year']):<6} {row['HPI_Index']:>12.0f} {yoy:>14} {row['Cumulative_Growth']:>13.1f}%")
        
        print("  " + "-" * 50)
        
        # ===== CITY-WISE ANALYSIS =====
        print("\n" + "=" * 70)
        print("  C. CITY-WISE HPI COMPARISON")
        print("=" * 70)
        
        cities = [col for col in city_df.columns if col != 'Year']
        city_stats = []
        
        for city in cities:
            first_idx = city_df[city].iloc[0]
            last_idx = city_df[city].iloc[-1]
            total_growth = ((last_idx - first_idx) / first_idx) * 100
            cagr_city = ((last_idx / first_idx) ** (1 / 15) - 1) * 100
            
            city_stats.append({
                'City': city,
                '2010': first_idx,
                '2025': last_idx,
                'Total_Growth': total_growth,
                'CAGR': cagr_city
            })
        
        city_stats_df = pd.DataFrame(city_stats).sort_values('CAGR', ascending=False)
        
        print(f"\n  ┌{'─'*14}┬{'─'*10}┬{'─'*10}┬{'─'*16}┬{'─'*10}┐")
        print(f"  │ {'City':<12} │ {'2010':>8} │ {'2025':>8} │ {'Total Growth':>14} │ {'CAGR':>8} │")
        print(f"  ├{'─'*14}┼{'─'*10}┼{'─'*10}┼{'─'*16}┼{'─'*10}┤")
        
        for _, row in city_stats_df.iterrows():
            print(f"  │ {row['City']:<12} │ {row['2010']:>8.0f} │ {row['2025']:>8.0f} │ {row['Total_Growth']:>13.1f}% │ {row['CAGR']:>7.2f}% │")
        
        print(f"  └{'─'*14}┴{'─'*10}┴{'─'*10}┴{'─'*16}┴{'─'*10}┘")
        
        # Visual comparison
        print(f"\n  City-wise CAGR (Visual Comparison):")
        print("  " + "-" * 55)
        
        for _, row in city_stats_df.iterrows():
            bar_length = int(row['CAGR'] * 3)
            bar = "█" * bar_length
            print(f"  {row['City']:<12} {bar} {row['CAGR']:.2f}%")
        
        print("  " + "-" * 55)
        
        # ===== INFLATION CALCULATIONS =====
        print("\n" + "=" * 70)
        print("  D. ALL INDIA INFLATION CALCULATIONS")
        print("=" * 70)
        
        first_year = yearly['Year'].iloc[0]
        last_year = yearly['Year'].iloc[-1]
        first_index = yearly['HPI_Index'].iloc[0]
        last_index = yearly['HPI_Index'].iloc[-1]
        total_years = last_year - first_year
        
        total_inflation = ((last_index - first_index) / first_index) * 100
        cagr = ((last_index / first_index) ** (1 / total_years) - 1) * 100
        avg_yoy = yearly['YoY_Change'].dropna().mean()
        
        growth_rates = (yearly['HPI_Index'] / yearly['HPI_Index'].shift(1)).dropna()
        geometric_mean = (np.prod(growth_rates) ** (1 / len(growth_rates)) - 1) * 100
        
        slope = np.polyfit(yearly['Year'], yearly['HPI_Index'], 1)[0]
        trend_inflation = (slope / yearly['HPI_Index'].mean()) * 100
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"\n  Starting Index ({first_year}):  {first_index:>8.0f}")
        print(f"  Ending Index ({last_year}):    {last_index:>8.0f}")
        print(f"  Absolute Change:             {last_index - first_index:>8.0f} points")
        
        print(f"\n  ┌{'─'*45}┬{'─'*18}┐")
        print(f"  │ {'Method':<43} │ {'Result':>16} │")
        print(f"  ├{'─'*45}┼{'─'*18}┤")
        print(f"  │ {'1. Total Inflation (End-Start)/Start':<43} │ {total_inflation:>15.2f}% │")
        print(f"  │ {'2. CAGR (Compound Annual Growth Rate)':<43} │ {cagr:>15.2f}% │")
        print(f"  │ {'3. Average Year-over-Year Change':<43} │ {avg_yoy:>15.2f}% │")
        print(f"  │ {'4. Geometric Mean of Growth Rates':<43} │ {geometric_mean:>15.2f}% │")
        print(f"  │ {'5. Linear Trend-based Inflation':<43} │ {trend_inflation:>15.2f}% │")
        print(f"  └{'─'*45}┴{'─'*18}┘")
        
        # ===== MARKET PHASES =====
        print("\n" + "=" * 70)
        print("  E. MARKET PHASES ANALYSIS")
        print("=" * 70)
        
        print(f"\n  Phase 1: Boom Period (2010-2014)")
        boom_growth = ((158 - 100) / 100) * 100
        boom_cagr = ((158 / 100) ** (1/4) - 1) * 100
        print(f"    HPI: 100 → 158 | Growth: {boom_growth:.1f}% | CAGR: {boom_cagr:.2f}%")
        print(f"    Characterized by: High demand, infrastructure growth")
        
        print(f"\n  Phase 2: Slowdown Period (2014-2019)")
        slow_growth = ((198 - 158) / 158) * 100
        slow_cagr = ((198 / 158) ** (1/5) - 1) * 100
        print(f"    HPI: 158 → 198 | Growth: {slow_growth:.1f}% | CAGR: {slow_cagr:.2f}%")
        print(f"    Characterized by: Demonetization, RERA, GST impact")
        
        print(f"\n  Phase 3: COVID Dip (2019-2020)")
        covid_growth = ((195 - 198) / 198) * 100
        print(f"    HPI: 198 → 195 | Growth: {covid_growth:.1f}%")
        print(f"    Characterized by: Pandemic lockdowns, uncertainty")
        
        print(f"\n  Phase 4: Recovery Period (2020-2025)")
        recovery_growth = ((287 - 195) / 195) * 100
        recovery_cagr = ((287 / 195) ** (1/5) - 1) * 100
        print(f"    HPI: 195 → 287 | Growth: {recovery_growth:.1f}% | CAGR: {recovery_cagr:.2f}%")
        print(f"    Characterized by: Low interest rates, WFH demand")
        
        # ===== FUTURE PROJECTIONS =====
        print("\n" + "=" * 70)
        print("  F. FUTURE PRICE PROJECTIONS")
        print("=" * 70)
        
        print(f"\n  Projecting using All India CAGR of {cagr:.2f}%:")
        print(f"\n  {'Year':<8} {'Projected HPI':>15} {'Growth from 2025':>18}")
        print("  " + "-" * 45)
        
        for i in range(1, 11):
            future_year = 2025 + i
            projected_hpi = 287 * ((1 + cagr/100) ** i)
            growth = ((projected_hpi - 287) / 287) * 100
            print(f"  {future_year:<8} {projected_hpi:>15.0f} {growth:>17.2f}%")
        
        print("  " + "-" * 45)
        
        print(f"\n  >>> REAL ESTATE INFLATION RATE: {cagr:.2f}% (CAGR)")
        
        # Best and worst city
        best_city = city_stats_df.iloc[0]
        worst_city = city_stats_df.iloc[-1]
        
        self.results['Real Estate'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'start_price': first_index,
            'end_price': last_index,
            'total_inflation': total_inflation,
            'cagr': cagr,
            'avg_yoy': avg_yoy,
            'geometric_mean': geometric_mean,
            'trend_inflation': trend_inflation,
            'best_city': best_city['City'],
            'best_city_cagr': best_city['CAGR'],
            'worst_city': worst_city['City'],
            'worst_city_cagr': worst_city['CAGR'],
            'cities_count': len(cities)
        }
        
    def print_final_comparison(self):
        """Print comprehensive final comparison"""
        print("\n" + "█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "  COMPREHENSIVE COMPARISON - ALL ASSET CLASSES".center(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)
        
        sorted_assets = sorted(self.results.items(), key=lambda x: x[1]['cagr'], reverse=True)
        
        # ===== SUMMARY TABLE =====
        print("\n" + "=" * 70)
        print("  A. INFLATION RATE COMPARISON")
        print("=" * 70)
        
        print(f"\n  ┌{'─'*16}┬{'─'*14}┬{'─'*8}┬{'─'*18}┬{'─'*12}┬{'─'*12}┐")
        print(f"  │ {'Asset':<14} │ {'Period':<12} │ {'Years':>6} │ {'Total Inflation':>16} │ {'CAGR':>10} │ {'Avg YoY':>10} │")
        print(f"  ├{'─'*16}┼{'─'*14}┼{'─'*8}┼{'─'*18}┼{'─'*12}┼{'─'*12}┤")
        
        for asset, data in sorted_assets:
            rank = "🥇" if asset == sorted_assets[0][0] else "🥈" if asset == sorted_assets[1][0] else "🥉"
            print(f"  │ {rank} {asset:<12} │ {data['period']:<12} │ {data['years']:>6} │ {data['total_inflation']:>15.2f}% │ {data['cagr']:>9.2f}% │ {data['avg_yoy']:>9.2f}% │")
        
        print(f"  └{'─'*16}┴{'─'*14}┴{'─'*8}┴{'─'*18}┴{'─'*12}┴{'─'*12}┘")
        
        # ===== VISUAL COMPARISON =====
        print("\n" + "=" * 70)
        print("  B. VISUAL COMPARISON (CAGR)")
        print("=" * 70)
        
        max_cagr = max(data['cagr'] for _, data in sorted_assets)
        
        print(f"\n  {'Asset':<14} {'CAGR':>8} {'Visualization':<40}")
        print("  " + "-" * 65)
        
        for asset, data in sorted_assets:
            bar_length = int((data['cagr'] / max_cagr) * 35)
            bar = "█" * bar_length
            print(f"  {asset:<14} {data['cagr']:>7.2f}% {bar}")
        
        print("  " + "-" * 65)
        
        # ===== INVESTMENT SIMULATION =====
        print("\n" + "=" * 70)
        print("  C. INVESTMENT GROWTH SIMULATION")
        print("=" * 70)
        
        initial_investments = [100000, 500000, 1000000]
        time_periods = [5, 10, 15, 20]
        
        for initial in initial_investments:
            print(f"\n  Investment: Rs. {initial:,}")
            print(f"  ┌{'─'*14}┬{'─'*14}┬{'─'*14}┬{'─'*14}┬{'─'*14}┐")
            print(f"  │ {'Asset':<12} │ {'5 Years':>12} │ {'10 Years':>12} │ {'15 Years':>12} │ {'20 Years':>12} │")
            print(f"  ├{'─'*14}┼{'─'*14}┼{'─'*14}┼{'─'*14}┼{'─'*14}┤")
            
            for asset, data in sorted_assets:
                vals = []
                for years in time_periods:
                    final = initial * ((1 + data['cagr']/100) ** years)
                    vals.append(f"Rs.{final/100000:>7.1f}L")
                print(f"  │ {asset:<12} │ {vals[0]:>12} │ {vals[1]:>12} │ {vals[2]:>12} │ {vals[3]:>12} │")
            
            print(f"  └{'─'*14}┴{'─'*14}┴{'─'*14}┴{'─'*14}┴{'─'*14}┘")
        
        # ===== KEY INSIGHTS =====
        print("\n" + "=" * 70)
        print("  D. KEY INSIGHTS")
        print("=" * 70)
        
        best = sorted_assets[0]
        worst = sorted_assets[-1]
        
        print(f"\n  1. HIGHEST INFLATION: {best[0]}")
        print(f"     CAGR: {best[1]['cagr']:.2f}% | Total Growth: {best[1]['total_inflation']:.2f}%")
        
        print(f"\n  2. LOWEST INFLATION: {worst[0]}")
        print(f"     CAGR: {worst[1]['cagr']:.2f}% | Total Growth: {worst[1]['total_inflation']:.2f}%")
        
        print(f"\n  3. DIFFERENCE IN RETURNS:")
        diff = best[1]['cagr'] - worst[1]['cagr']
        print(f"     {best[0]} vs {worst[0]}: {diff:.2f} percentage points per year")
        
        # Calculate 10-year difference
        initial = 100000
        best_10yr = initial * ((1 + best[1]['cagr']/100) ** 10)
        worst_10yr = initial * ((1 + worst[1]['cagr']/100) ** 10)
        diff_10yr = best_10yr - worst_10yr
        print(f"     Rs. 1L invested for 10 years: Difference of Rs. {diff_10yr:,.0f}")
        
        print(f"\n  4. RISK CONSIDERATIONS:")
        print(f"     • Gold: High liquidity, no maintenance, hedge against inflation")
        print(f"     • Car: Depreciating asset (resale), utility value")
        print(f"     • Real Estate: Low liquidity, rental income potential, high entry cost")
        
        # ===== FINAL RANKING =====
        print("\n" + "=" * 70)
        print("  E. FINAL RANKING")
        print("=" * 70)
        
        print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║                     INFLATION RATES (CAGR)                       ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║                                                                  ║
  ║   🥇  {sorted_assets[0][0]:<18}    {sorted_assets[0][1]['cagr']:>6.2f}% per year              ║
  ║                                                                  ║
  ║   🥈  {sorted_assets[1][0]:<18}    {sorted_assets[1][1]['cagr']:>6.2f}% per year              ║
  ║                                                                  ║
  ║   🥉  {sorted_assets[2][0]:<18}    {sorted_assets[2][1]['cagr']:>6.2f}% per year              ║
  ║                                                                  ║
  ╚══════════════════════════════════════════════════════════════════╝
""")
        
    def run_analysis(self):
        """Run complete detailed analysis"""
        print("\n" + "█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "  DETAILED INVESTMENT ANALYSIS - GOLD, CAR & REAL ESTATE".center(78) + "█")
        print("█" + "  Comprehensive Inflation Rate Comparison".center(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)
        
        # Run detailed analysis for each asset
        self.analyze_gold_detailed()
        self.analyze_car_detailed()
        self.analyze_real_estate_detailed()
        
        # Print comprehensive comparison
        self.print_final_comparison()
        
        print("\n" + "█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "  ANALYSIS COMPLETE!".center(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)


def main():
    excel_path = r"c:\Users\Mahina Varma\OneDrive\Desktop\BE Project Datasets\BE Project Implementation\money_mentor\src\combined_dataset_20251005_175959.xlsx"
    
    analyzer = DetailedInvestmentAnalyzer(excel_path)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
