"""
Combined Investment Analysis - Gold, Car & Real Estate
Systematic comparison of inflation rates across all three asset classes
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class CombinedInvestmentAnalyzer:
    def __init__(self, excel_path):
        self.excel_path = excel_path
        self.results = {}
        
    def analyze_gold(self):
        """Analyze Gold inflation"""
        print("\n" + "=" * 80)
        print("  1. GOLD INFLATION ANALYSIS")
        print("=" * 80)
        
        # Load gold data
        gold_data = pd.read_excel(self.excel_path, sheet_name='Gold_Data')
        gold_data['Date'] = pd.to_datetime(gold_data['Date'])
        gold_data['Year'] = gold_data['Date'].dt.year
        
        # Yearly aggregation
        yearly = gold_data.groupby('Year')['Price'].agg(['mean', 'min', 'max']).reset_index()
        yearly.columns = ['Year', 'Avg_Price', 'Min_Price', 'Max_Price']
        yearly['YoY_Change'] = yearly['Avg_Price'].pct_change() * 100
        
        # Calculate metrics
        first_year = yearly['Year'].iloc[0]
        last_year = yearly['Year'].iloc[-1]
        first_price = yearly['Avg_Price'].iloc[0]
        last_price = yearly['Avg_Price'].iloc[-1]
        total_years = last_year - first_year
        
        total_inflation = ((last_price - first_price) / first_price) * 100
        cagr = ((last_price / first_price) ** (1 / total_years) - 1) * 100
        avg_yoy = yearly['YoY_Change'].dropna().mean()
        
        # Display yearly data
        print(f"\n  Data Source: Excel Dataset")
        print(f"  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"  Total Records: {len(gold_data)}")
        
        print(f"\n  {'Year':<8} {'Avg Price (Rs.)':>15} {'Min':>12} {'Max':>12} {'YoY':>10}")
        print("  " + "-" * 60)
        for _, row in yearly.iterrows():
            yoy = f"{row['YoY_Change']:+.2f}%" if pd.notna(row['YoY_Change']) else "N/A"
            print(f"  {int(row['Year']):<8} {row['Avg_Price']:>15,.0f} {row['Min_Price']:>12,.0f} {row['Max_Price']:>12,.0f} {yoy:>10}")
        print("  " + "-" * 60)
        
        print(f"\n  Starting Price (Avg {first_year}): Rs. {first_price:,.2f}")
        print(f"  Ending Price (Avg {last_year}):   Rs. {last_price:,.2f}")
        
        print(f"\n  +{'-'*40}+{'-'*15}+")
        print(f"  | {'Metric':<38} | {'Value':>13} |")
        print(f"  +{'-'*40}+{'-'*15}+")
        print(f"  | {'Total Inflation':<38} | {total_inflation:>12.2f}% |")
        print(f"  | {'CAGR (Compound Annual Growth Rate)':<38} | {cagr:>12.2f}% |")
        print(f"  | {'Average Year-over-Year Change':<38} | {avg_yoy:>12.2f}% |")
        print(f"  +{'-'*40}+{'-'*15}+")
        
        print(f"\n  >>> GOLD INFLATION RATE: {cagr:.2f}% per year")
        
        self.results['Gold'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'start_price': first_price,
            'end_price': last_price,
            'total_inflation': total_inflation,
            'cagr': cagr,
            'avg_yoy': avg_yoy,
            'data_source': 'Excel Dataset'
        }
        
    def analyze_car(self):
        """Analyze Car price inflation"""
        print("\n" + "=" * 80)
        print("  2. CAR PRICE INFLATION ANALYSIS")
        print("=" * 80)
        
        # Load car data
        car_data = pd.read_excel(self.excel_path, sheet_name='Car Data')
        
        # Yearly aggregation
        yearly = car_data.groupby('year')['selling_price'].agg(['mean', 'min', 'max', 'count']).reset_index()
        yearly.columns = ['Year', 'Avg_Price', 'Min_Price', 'Max_Price', 'Count']
        yearly['YoY_Change'] = yearly['Avg_Price'].pct_change() * 100
        
        # Calculate metrics
        first_year = yearly['Year'].iloc[0]
        last_year = yearly['Year'].iloc[-1]
        first_price = yearly['Avg_Price'].iloc[0]
        last_price = yearly['Avg_Price'].iloc[-1]
        total_years = last_year - first_year
        
        total_inflation = ((last_price - first_price) / first_price) * 100
        cagr = ((last_price / first_price) ** (1 / total_years) - 1) * 100
        avg_yoy = yearly['YoY_Change'].dropna().mean()
        
        # Display yearly data
        print(f"\n  Data Source: Excel Dataset")
        print(f"  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"  Total Records: {len(car_data)}")
        
        print(f"\n  {'Year':<8} {'Avg Price (Rs.)':>15} {'Count':>8} {'YoY':>12}")
        print("  " + "-" * 48)
        for _, row in yearly.iterrows():
            yoy = f"{row['YoY_Change']:+.2f}%" if pd.notna(row['YoY_Change']) else "N/A"
            print(f"  {int(row['Year']):<8} {row['Avg_Price']:>15,.0f} {int(row['Count']):>8} {yoy:>12}")
        print("  " + "-" * 48)
        
        print(f"\n  Starting Price (Avg {first_year}): Rs. {first_price:,.2f}")
        print(f"  Ending Price (Avg {last_year}):   Rs. {last_price:,.2f}")
        
        print(f"\n  +{'-'*40}+{'-'*15}+")
        print(f"  | {'Metric':<38} | {'Value':>13} |")
        print(f"  +{'-'*40}+{'-'*15}+")
        print(f"  | {'Total Inflation':<38} | {total_inflation:>12.2f}% |")
        print(f"  | {'CAGR (Compound Annual Growth Rate)':<38} | {cagr:>12.2f}% |")
        print(f"  | {'Average Year-over-Year Change':<38} | {avg_yoy:>12.2f}% |")
        print(f"  +{'-'*40}+{'-'*15}+")
        
        print(f"\n  >>> CAR PRICE INFLATION RATE: {cagr:.2f}% per year")
        
        self.results['Car'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'start_price': first_price,
            'end_price': last_price,
            'total_inflation': total_inflation,
            'cagr': cagr,
            'avg_yoy': avg_yoy,
            'data_source': 'Excel Dataset'
        }
        
    def analyze_real_estate(self):
        """Analyze Real Estate inflation using HPI data"""
        print("\n" + "=" * 80)
        print("  3. REAL ESTATE INFLATION ANALYSIS")
        print("=" * 80)
        
        # RBI/NHB Housing Price Index Data
        hpi_data = {
            'Year': [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            'HPI_Index': [100, 111, 126, 143, 158, 167, 175, 183, 191, 198, 195, 203, 218, 237, 261, 287]
        }
        
        yearly = pd.DataFrame(hpi_data)
        yearly['YoY_Change'] = yearly['HPI_Index'].pct_change() * 100
        
        # Calculate metrics
        first_year = yearly['Year'].iloc[0]
        last_year = yearly['Year'].iloc[-1]
        first_index = yearly['HPI_Index'].iloc[0]
        last_index = yearly['HPI_Index'].iloc[-1]
        total_years = last_year - first_year
        
        total_inflation = ((last_index - first_index) / first_index) * 100
        cagr = ((last_index / first_index) ** (1 / total_years) - 1) * 100
        avg_yoy = yearly['YoY_Change'].dropna().mean()
        
        # Display yearly data
        print(f"\n  Data Source: RBI/NHB Housing Price Index")
        print(f"  Period: {first_year} - {last_year} ({total_years} years)")
        print(f"  Base Year: 2010 = 100")
        
        print(f"\n  {'Year':<8} {'HPI Index':>12} {'YoY Change':>14}")
        print("  " + "-" * 38)
        for _, row in yearly.iterrows():
            yoy = f"{row['YoY_Change']:+.2f}%" if pd.notna(row['YoY_Change']) else "N/A"
            print(f"  {int(row['Year']):<8} {row['HPI_Index']:>12.0f} {yoy:>14}")
        print("  " + "-" * 38)
        
        print(f"\n  Starting Index ({first_year}): {first_index:.0f}")
        print(f"  Ending Index ({last_year}):   {last_index:.0f}")
        
        print(f"\n  +{'-'*40}+{'-'*15}+")
        print(f"  | {'Metric':<38} | {'Value':>13} |")
        print(f"  +{'-'*40}+{'-'*15}+")
        print(f"  | {'Total Inflation':<38} | {total_inflation:>12.2f}% |")
        print(f"  | {'CAGR (Compound Annual Growth Rate)':<38} | {cagr:>12.2f}% |")
        print(f"  | {'Average Year-over-Year Change':<38} | {avg_yoy:>12.2f}% |")
        print(f"  +{'-'*40}+{'-'*15}+")
        
        # City-wise summary
        print(f"\n  City-wise CAGR (2010-2025):")
        city_cagr = [
            ('Hyderabad', 9.72), ('Bangalore', 8.87), ('Mumbai', 7.88),
            ('Pune', 7.88), ('Delhi', 7.83), ('Chennai', 7.11),
            ('Ahmedabad', 7.11), ('Kolkata', 6.18)
        ]
        for city, rate in city_cagr:
            bar = "█" * int(rate)
            print(f"  {city:<12} {rate:>5.2f}% {bar}")
        
        print(f"\n  >>> REAL ESTATE INFLATION RATE: {cagr:.2f}% per year")
        
        self.results['Real Estate'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'start_price': first_index,
            'end_price': last_index,
            'total_inflation': total_inflation,
            'cagr': cagr,
            'avg_yoy': avg_yoy,
            'data_source': 'RBI/NHB HPI'
        }
        
    def print_comparison(self):
        """Print systematic comparison of all assets"""
        print("\n" + "=" * 80)
        print("  SYSTEMATIC COMPARISON - ALL ASSET CLASSES")
        print("=" * 80)
        
        # Sort by CAGR
        sorted_assets = sorted(self.results.items(), key=lambda x: x[1]['cagr'], reverse=True)
        
        # Summary Table
        print(f"\n  +{'-'*16}+{'-'*14}+{'-'*10}+{'-'*18}+{'-'*12}+{'-'*12}+")
        print(f"  | {'Asset':<14} | {'Period':<12} | {'Years':>8} | {'Total Inflation':>16} | {'CAGR':>10} | {'Avg YoY':>10} |")
        print(f"  +{'-'*16}+{'-'*14}+{'-'*10}+{'-'*18}+{'-'*12}+{'-'*12}+")
        
        for asset, data in sorted_assets:
            print(f"  | {asset:<14} | {data['period']:<12} | {data['years']:>8} | {data['total_inflation']:>15.2f}% | {data['cagr']:>9.2f}% | {data['avg_yoy']:>9.2f}% |")
        
        print(f"  +{'-'*16}+{'-'*14}+{'-'*10}+{'-'*18}+{'-'*12}+{'-'*12}+")
        
        # Visual comparison
        print(f"\n  CAGR Comparison (Visual):")
        print("  " + "-" * 50)
        
        max_cagr = max(data['cagr'] for _, data in sorted_assets)
        
        for asset, data in sorted_assets:
            bar_length = int((data['cagr'] / max_cagr) * 30)
            bar = "█" * bar_length
            print(f"  {asset:<14} {bar} {data['cagr']:.2f}%")
        
        print("  " + "-" * 50)
        
        # Key Insights
        print(f"\n  KEY INSIGHTS:")
        print("  " + "-" * 50)
        
        best_asset = sorted_assets[0]
        worst_asset = sorted_assets[-1]
        
        print(f"  ✓ Highest Inflation: {best_asset[0]} ({best_asset[1]['cagr']:.2f}% CAGR)")
        print(f"  ✓ Lowest Inflation:  {worst_asset[0]} ({worst_asset[1]['cagr']:.2f}% CAGR)")
        
        # Calculate difference
        diff = best_asset[1]['cagr'] - worst_asset[1]['cagr']
        print(f"  ✓ Difference:        {diff:.2f} percentage points")
        
        # Investment growth comparison (Rs. 1 Lakh over 10 years)
        print(f"\n  INVESTMENT GROWTH SIMULATION:")
        print(f"  If you invested Rs. 1,00,000 for 10 years:")
        print("  " + "-" * 50)
        
        initial = 100000
        for asset, data in sorted_assets:
            final = initial * ((1 + data['cagr']/100) ** 10)
            gain = final - initial
            print(f"  {asset:<14} → Rs. {final:>12,.0f} (Gain: Rs. {gain:>10,.0f})")
        
        print("  " + "-" * 50)
        
    def print_methodology(self):
        """Print methodology explanation"""
        print("\n" + "=" * 80)
        print("  METHODOLOGY: CAGR CALCULATION")
        print("=" * 80)
        
        print("""
  CAGR (Compound Annual Growth Rate) Formula:
  ─────────────────────────────────────────────
  
                    ┌              ┐ (1/n)
         CAGR  =   │ Ending Value  │        - 1
                   │ ─────────────│
                   │ Starting Value│
                    └              ┘
  
  Where:
    • Ending Value   = Final price/index
    • Starting Value = Initial price/index  
    • n              = Number of years
  
  Why CAGR is Used:
  ─────────────────
  1. Accounts for compounding effect
  2. Provides smooth annualized return
  3. Easy comparison across different time periods
  4. Industry standard for investment analysis
  
  Example (Gold):
  ───────────────
  Starting (2014): Rs. 28,101
  Ending (2026):   Rs. 135,782
  Years:           12
  
  CAGR = (135,782 / 28,101)^(1/12) - 1
       = (4.8319)^(0.0833) - 1
       = 1.1403 - 1
       = 0.1403
       = 14.03%
""")
        
    def run_analysis(self):
        """Run complete combined analysis"""
        print("\n" + "█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "    COMBINED INVESTMENT ANALYSIS - GOLD, CAR & REAL ESTATE".center(78) + "█")
        print("█" + "    Systematic Comparison of Inflation Rates".center(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)
        
        # Analyze each asset
        self.analyze_gold()
        self.analyze_car()
        self.analyze_real_estate()
        
        # Print comparison
        self.print_comparison()
        
        # Print methodology
        self.print_methodology()
        
        # Final summary
        print("\n" + "=" * 80)
        print("  FINAL SUMMARY")
        print("=" * 80)
        
        sorted_assets = sorted(self.results.items(), key=lambda x: x[1]['cagr'], reverse=True)
        
        print(f"\n  ╔{'═'*50}╗")
        print(f"  ║{'INFLATION RATES (CAGR)':^50}║")
        print(f"  ╠{'═'*50}╣")
        
        for i, (asset, data) in enumerate(sorted_assets, 1):
            rank = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            print(f"  ║  {rank} {asset:<20} {data['cagr']:>8.2f}% per year      ║")
        
        print(f"  ╚{'═'*50}╝")
        
        print("\n" + "=" * 80)
        print("  ANALYSIS COMPLETE!")
        print("=" * 80)


def main():
    excel_path = r"c:\Users\Mahina Varma\OneDrive\Desktop\BE Project Datasets\BE Project Implementation\money_mentor\src\combined_dataset_20251005_175959.xlsx"
    
    analyzer = CombinedInvestmentAnalyzer(excel_path)
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
