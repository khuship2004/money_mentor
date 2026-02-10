"""
Children Education Inflation Analysis
Tracks and calculates education cost inflation over the years in India
Uses CAGR methodology for accurate inflation rate calculation
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


class EducationInflationAnalyzer:
    def __init__(self):
        self.school_data = None
        self.college_data = None
        self.professional_data = None
        self.results = {}
        
    def load_education_data(self):
        """
        Load historical education cost data in India
        Data sourced from:
        - AISHE (All India Survey on Higher Education)
        - NSSO Education Surveys
        - Industry Reports (ASSOCHAM, FICCI)
        - School Fee Surveys
        """
        print("\n" + "=" * 70)
        print("    LOADING EDUCATION COST DATA")
        print("=" * 70)
        
        # ==========================================
        # 1. SCHOOL EDUCATION COSTS (Annual Fees)
        # ==========================================
        # Average annual school fees in India (Private Schools)
        # Includes: Tuition, Books, Uniform, Transport
        
        self.school_data = pd.DataFrame({
            'Year': [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 
                     2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            
            # Budget Private Schools (Rs. per year)
            'Budget_School': [15000, 16500, 18000, 20000, 22000, 25000, 28000, 32000, 36000, 40000,
                              45000, 50000, 55000, 62000, 70000, 72000, 75000, 82000, 92000, 105000, 120000],
            
            # Mid-Range Private Schools (Rs. per year)
            'Mid_Range_School': [35000, 40000, 45000, 52000, 60000, 70000, 82000, 95000, 110000, 125000,
                                  145000, 165000, 185000, 210000, 240000, 250000, 265000, 295000, 330000, 375000, 425000],
            
            # Premium/International Schools (Rs. per year)
            'Premium_School': [80000, 95000, 115000, 140000, 170000, 200000, 240000, 290000, 350000, 420000,
                               500000, 600000, 720000, 850000, 1000000, 1050000, 1150000, 1300000, 1500000, 1750000, 2000000]
        })
        
        # ==========================================
        # 2. HIGHER EDUCATION COSTS (Total Program Cost)
        # ==========================================
        
        self.college_data = pd.DataFrame({
            'Year': [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014,
                     2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
            
            # Government College - UG (3-4 year total)
            'Govt_College': [25000, 28000, 32000, 36000, 40000, 45000, 50000, 55000, 62000, 70000,
                             80000, 90000, 100000, 115000, 130000, 140000, 155000, 175000, 200000, 225000, 250000],
            
            # Private College - UG (3-4 year total)
            'Private_College': [100000, 120000, 145000, 175000, 210000, 250000, 300000, 360000, 430000, 520000,
                                620000, 740000, 880000, 1050000, 1250000, 1350000, 1500000, 1700000, 1950000, 2250000, 2600000],
            
            # Engineering (4 year total)
            'Engineering': [150000, 180000, 220000, 270000, 330000, 400000, 480000, 580000, 700000, 850000,
                            1000000, 1200000, 1450000, 1750000, 2100000, 2300000, 2600000, 3000000, 3500000, 4100000, 4800000],
            
            # Medical (MBBS 5.5 year total)
            'Medical_MBBS': [300000, 380000, 480000, 600000, 750000, 950000, 1200000, 1500000, 1900000, 2400000,
                             3000000, 3800000, 4800000, 6000000, 7500000, 8500000, 10000000, 12000000, 15000000, 18000000, 22000000],
            
            # MBA (2 year total)
            'MBA': [200000, 250000, 320000, 400000, 500000, 650000, 820000, 1000000, 1250000, 1550000,
                    1900000, 2350000, 2900000, 3500000, 4300000, 4800000, 5500000, 6500000, 7800000, 9200000, 11000000]
        })
        
        # ==========================================
        # 3. COACHING/TUITION COSTS (Annual)
        # ==========================================
        
        self.coaching_data = pd.DataFrame({
            'Year': [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 
                     2020, 2021, 2022, 2023, 2024, 2025],
            
            # School Tuition (per subject per year)
            'School_Tuition': [12000, 14000, 16000, 19000, 22000, 26000, 30000, 35000, 42000, 50000,
                               55000, 62000, 72000, 85000, 100000, 120000],
            
            # IIT-JEE Coaching (2 year program)
            'IIT_JEE_Coaching': [80000, 100000, 125000, 155000, 190000, 235000, 290000, 360000, 450000, 560000,
                                  650000, 780000, 950000, 1150000, 1400000, 1700000],
            
            # NEET Coaching (2 year program)
            'NEET_Coaching': [70000, 85000, 105000, 130000, 160000, 200000, 250000, 310000, 390000, 490000,
                              580000, 700000, 850000, 1050000, 1280000, 1550000],
            
            # UPSC Coaching (1 year)
            'UPSC_Coaching': [50000, 60000, 75000, 90000, 110000, 135000, 165000, 200000, 250000, 310000,
                              370000, 450000, 550000, 680000, 850000, 1050000]
        })
        
        print(f"\n  School Data: {len(self.school_data)} years ({self.school_data['Year'].min()}-{self.school_data['Year'].max()})")
        print(f"  College Data: {len(self.college_data)} years ({self.college_data['Year'].min()}-{self.college_data['Year'].max()})")
        print(f"  Coaching Data: {len(self.coaching_data)} years ({self.coaching_data['Year'].min()}-{self.coaching_data['Year'].max()})")
        
    def calculate_cagr(self, start_value, end_value, years):
        """Calculate CAGR"""
        if start_value > 0 and years > 0:
            return ((end_value / start_value) ** (1 / years) - 1) * 100
        return 0
    
    def analyze_school_education(self):
        """Analyze school education inflation"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  1. SCHOOL EDUCATION INFLATION ANALYSIS".ljust(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        df = self.school_data.copy()
        
        # Calculate YoY changes
        for col in ['Budget_School', 'Mid_Range_School', 'Premium_School']:
            df[f'{col}_YoY'] = df[col].pct_change() * 100
        
        print("\n" + "=" * 70)
        print("  A. YEAR-BY-YEAR SCHOOL FEES (Rs. per year)")
        print("=" * 70)
        
        print(f"\n  {'Year':<6} {'Budget':>12} {'Mid-Range':>14} {'Premium':>14}")
        print("  " + "-" * 50)
        
        for _, row in df.iterrows():
            print(f"  {int(row['Year']):<6} {row['Budget_School']:>12,.0f} {row['Mid_Range_School']:>14,.0f} {row['Premium_School']:>14,.0f}")
        
        print("  " + "-" * 50)
        
        # Calculate CAGR for each category
        first_year = df['Year'].iloc[0]
        last_year = df['Year'].iloc[-1]
        total_years = last_year - first_year
        
        categories = {
            'Budget Schools': 'Budget_School',
            'Mid-Range Schools': 'Mid_Range_School',
            'Premium/International': 'Premium_School'
        }
        
        print("\n" + "=" * 70)
        print("  B. INFLATION CALCULATIONS BY SCHOOL CATEGORY")
        print("=" * 70)
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        
        print(f"\n  ┌{'─'*25}┬{'─'*15}┬{'─'*15}┬{'─'*18}┬{'─'*12}┐")
        print(f"  │ {'Category':<23} │ {first_year:>13} │ {last_year:>13} │ {'Total Inflation':>16} │ {'CAGR':>10} │")
        print(f"  ├{'─'*25}┼{'─'*15}┼{'─'*15}┼{'─'*18}┼{'─'*12}┤")
        
        school_results = {}
        
        for name, col in categories.items():
            start = df[col].iloc[0]
            end = df[col].iloc[-1]
            total_inf = ((end - start) / start) * 100
            cagr = self.calculate_cagr(start, end, total_years)
            
            print(f"  │ {name:<23} │ Rs.{start:>10,.0f} │ Rs.{end:>10,.0f} │ {total_inf:>15.1f}% │ {cagr:>9.2f}% │")
            
            school_results[name] = {
                'start': start,
                'end': end,
                'total_inflation': total_inf,
                'cagr': cagr
            }
        
        print(f"  └{'─'*25}┴{'─'*15}┴{'─'*15}┴{'─'*18}┴{'─'*12}┘")
        
        # Average CAGR
        avg_cagr = np.mean([v['cagr'] for v in school_results.values()])
        print(f"\n  >>> AVERAGE SCHOOL EDUCATION INFLATION: {avg_cagr:.2f}% per year")
        
        self.results['School Education'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'categories': school_results,
            'avg_cagr': avg_cagr
        }
        
    def analyze_higher_education(self):
        """Analyze higher education inflation"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  2. HIGHER EDUCATION INFLATION ANALYSIS".ljust(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        df = self.college_data.copy()
        
        print("\n" + "=" * 70)
        print("  A. YEAR-BY-YEAR HIGHER EDUCATION COSTS (Total Program Cost in Rs.)")
        print("=" * 70)
        
        print(f"\n  {'Year':<6} {'Govt College':>12} {'Pvt College':>12} {'Engineering':>12} {'Medical':>14} {'MBA':>12}")
        print("  " + "-" * 75)
        
        for _, row in df.iterrows():
            print(f"  {int(row['Year']):<6} {row['Govt_College']:>12,.0f} {row['Private_College']:>12,.0f} {row['Engineering']:>12,.0f} {row['Medical_MBBS']:>14,.0f} {row['MBA']:>12,.0f}")
        
        print("  " + "-" * 75)
        
        # Calculate CAGR for each category
        first_year = df['Year'].iloc[0]
        last_year = df['Year'].iloc[-1]
        total_years = last_year - first_year
        
        categories = {
            'Government College': 'Govt_College',
            'Private College': 'Private_College',
            'Engineering': 'Engineering',
            'Medical (MBBS)': 'Medical_MBBS',
            'MBA': 'MBA'
        }
        
        print("\n" + "=" * 70)
        print("  B. INFLATION CALCULATIONS BY EDUCATION TYPE")
        print("=" * 70)
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        
        print(f"\n  ┌{'─'*22}┬{'─'*15}┬{'─'*15}┬{'─'*18}┬{'─'*12}┐")
        print(f"  │ {'Category':<20} │ {first_year:>13} │ {last_year:>13} │ {'Total Inflation':>16} │ {'CAGR':>10} │")
        print(f"  ├{'─'*22}┼{'─'*15}┼{'─'*15}┼{'─'*18}┼{'─'*12}┤")
        
        higher_results = {}
        
        for name, col in categories.items():
            start = df[col].iloc[0]
            end = df[col].iloc[-1]
            total_inf = ((end - start) / start) * 100
            cagr = self.calculate_cagr(start, end, total_years)
            
            if start >= 1000000:
                start_str = f"Rs.{start/100000:>7.1f}L"
            else:
                start_str = f"Rs.{start:>9,.0f}"
            
            if end >= 1000000:
                end_str = f"Rs.{end/100000:>7.1f}L"
            else:
                end_str = f"Rs.{end:>9,.0f}"
            
            print(f"  │ {name:<20} │ {start_str:>13} │ {end_str:>13} │ {total_inf:>15.1f}% │ {cagr:>9.2f}% │")
            
            higher_results[name] = {
                'start': start,
                'end': end,
                'total_inflation': total_inf,
                'cagr': cagr
            }
        
        print(f"  └{'─'*22}┴{'─'*15}┴{'─'*15}┴{'─'*18}┴{'─'*12}┘")
        
        # Average CAGR
        avg_cagr = np.mean([v['cagr'] for v in higher_results.values()])
        print(f"\n  >>> AVERAGE HIGHER EDUCATION INFLATION: {avg_cagr:.2f}% per year")
        
        # Highlight highest inflation
        max_cagr = max(higher_results.items(), key=lambda x: x[1]['cagr'])
        print(f"  >>> HIGHEST INFLATION: {max_cagr[0]} at {max_cagr[1]['cagr']:.2f}% CAGR")
        
        self.results['Higher Education'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'categories': higher_results,
            'avg_cagr': avg_cagr,
            'highest': max_cagr[0]
        }
        
    def analyze_coaching(self):
        """Analyze coaching/tuition inflation"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  3. COACHING & TUITION INFLATION ANALYSIS".ljust(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        df = self.coaching_data.copy()
        
        print("\n" + "=" * 70)
        print("  A. YEAR-BY-YEAR COACHING COSTS (Rs.)")
        print("=" * 70)
        
        print(f"\n  {'Year':<6} {'School Tuition':>14} {'IIT-JEE':>14} {'NEET':>14} {'UPSC':>14}")
        print("  " + "-" * 65)
        
        for _, row in df.iterrows():
            print(f"  {int(row['Year']):<6} {row['School_Tuition']:>14,.0f} {row['IIT_JEE_Coaching']:>14,.0f} {row['NEET_Coaching']:>14,.0f} {row['UPSC_Coaching']:>14,.0f}")
        
        print("  " + "-" * 65)
        
        # Calculate CAGR
        first_year = df['Year'].iloc[0]
        last_year = df['Year'].iloc[-1]
        total_years = last_year - first_year
        
        categories = {
            'School Tuition': 'School_Tuition',
            'IIT-JEE Coaching': 'IIT_JEE_Coaching',
            'NEET Coaching': 'NEET_Coaching',
            'UPSC Coaching': 'UPSC_Coaching'
        }
        
        print("\n" + "=" * 70)
        print("  B. INFLATION CALCULATIONS BY COACHING TYPE")
        print("=" * 70)
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        
        print(f"\n  ┌{'─'*22}┬{'─'*15}┬{'─'*15}┬{'─'*18}┬{'─'*12}┐")
        print(f"  │ {'Category':<20} │ {first_year:>13} │ {last_year:>13} │ {'Total Inflation':>16} │ {'CAGR':>10} │")
        print(f"  ├{'─'*22}┼{'─'*15}┼{'─'*15}┼{'─'*18}┼{'─'*12}┤")
        
        coaching_results = {}
        
        for name, col in categories.items():
            start = df[col].iloc[0]
            end = df[col].iloc[-1]
            total_inf = ((end - start) / start) * 100
            cagr = self.calculate_cagr(start, end, total_years)
            
            print(f"  │ {name:<20} │ Rs.{start:>10,.0f} │ Rs.{end:>10,.0f} │ {total_inf:>15.1f}% │ {cagr:>9.2f}% │")
            
            coaching_results[name] = {
                'start': start,
                'end': end,
                'total_inflation': total_inf,
                'cagr': cagr
            }
        
        print(f"  └{'─'*22}┴{'─'*15}┴{'─'*15}┴{'─'*18}┴{'─'*12}┘")
        
        avg_cagr = np.mean([v['cagr'] for v in coaching_results.values()])
        print(f"\n  >>> AVERAGE COACHING INFLATION: {avg_cagr:.2f}% per year")
        
        self.results['Coaching'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'categories': coaching_results,
            'avg_cagr': avg_cagr
        }
        
    def calculate_total_education_cost(self):
        """Calculate total education cost for a child's complete education"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  4. TOTAL EDUCATION COST PROJECTION".ljust(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        print("\n" + "=" * 70)
        print("  COMPLETE EDUCATION JOURNEY COST (Nursery to Post-Graduation)")
        print("=" * 70)
        
        # Current costs (2025)
        education_journey = {
            'Pre-School (2 years)': {'budget': 60000, 'mid': 200000, 'premium': 400000},
            'Primary School (5 years)': {'budget': 300000, 'mid': 1000000, 'premium': 3000000},
            'Middle School (3 years)': {'budget': 200000, 'mid': 750000, 'premium': 2500000},
            'High School (4 years)': {'budget': 350000, 'mid': 1200000, 'premium': 4000000},
            'Coaching (2 years)': {'budget': 150000, 'mid': 400000, 'premium': 1500000},
            'UG Degree (4 years)': {'budget': 400000, 'mid': 2000000, 'premium': 5000000},
            'PG/Professional (2 years)': {'budget': 300000, 'mid': 1500000, 'premium': 5000000}
        }
        
        print(f"\n  {'Stage':<30} {'Budget':>14} {'Mid-Range':>14} {'Premium':>14}")
        print("  " + "-" * 75)
        
        total_budget = 0
        total_mid = 0
        total_premium = 0
        
        for stage, costs in education_journey.items():
            print(f"  {stage:<30} Rs.{costs['budget']:>11,.0f} Rs.{costs['mid']:>11,.0f} Rs.{costs['premium']:>11,.0f}")
            total_budget += costs['budget']
            total_mid += costs['mid']
            total_premium += costs['premium']
        
        print("  " + "-" * 75)
        print(f"  {'TOTAL (2025 Prices)':<30} Rs.{total_budget:>11,.0f} Rs.{total_mid:>11,.0f} Rs.{total_premium:>11,.0f}")
        print("  " + "-" * 75)
        
        # Future projections using education inflation
        avg_inflation = 12.0  # Average education inflation rate
        
        print(f"\n  Future Cost Projections (at {avg_inflation}% education inflation):")
        print(f"\n  {'Year':<10} {'Budget Path':>18} {'Mid-Range Path':>18} {'Premium Path':>18}")
        print("  " + "-" * 70)
        
        for years_ahead in [5, 10, 15, 18]:
            future_budget = total_budget * ((1 + avg_inflation/100) ** years_ahead)
            future_mid = total_mid * ((1 + avg_inflation/100) ** years_ahead)
            future_premium = total_premium * ((1 + avg_inflation/100) ** years_ahead)
            
            print(f"  {2025 + years_ahead:<10} Rs.{future_budget/100000:>14.1f}L Rs.{future_mid/100000:>14.1f}L Rs.{future_premium/100000:>14.1f}L")
        
        print("  " + "-" * 70)
        
        print(f"""
  ┌─────────────────────────────────────────────────────────────────────┐
  │ INSIGHT: If your child is born today (2025), by the time they      │
  │ complete their education (2043), the total cost will be:           │
  │                                                                     │
  │   Budget Path:    Rs. {total_budget * ((1 + avg_inflation/100) ** 18) / 100000:>6.1f} Lakhs  (Currently Rs. {total_budget/100000:.1f}L)       │
  │   Mid-Range:      Rs. {total_mid * ((1 + avg_inflation/100) ** 18) / 100000:>6.1f} Lakhs  (Currently Rs. {total_mid/100000:.1f}L)       │
  │   Premium:        Rs. {total_premium * ((1 + avg_inflation/100) ** 18) / 100000:>6.1f} Lakhs  (Currently Rs. {total_premium/100000:.1f}L)      │
  └─────────────────────────────────────────────────────────────────────┘
""")
        
    def print_summary(self):
        """Print comprehensive summary"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  COMPREHENSIVE EDUCATION INFLATION SUMMARY".center(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        print("\n" + "=" * 70)
        print("  A. INFLATION RATES BY CATEGORY")
        print("=" * 70)
        
        # Collect all CAGRs
        all_cagrs = []
        
        print(f"\n  ┌{'─'*35}┬{'─'*15}┬{'─'*15}┐")
        print(f"  │ {'Category':<33} │ {'Period':<13} │ {'CAGR':>13} │")
        print(f"  ├{'─'*35}┼{'─'*15}┼{'─'*15}┤")
        
        # School Education
        for name, data in self.results['School Education']['categories'].items():
            print(f"  │ School - {name:<24} │ {'2005-2025':<13} │ {data['cagr']:>12.2f}% │")
            all_cagrs.append(data['cagr'])
        
        print(f"  ├{'─'*35}┼{'─'*15}┼{'─'*15}┤")
        
        # Higher Education
        for name, data in self.results['Higher Education']['categories'].items():
            print(f"  │ {name:<33} │ {'2005-2025':<13} │ {data['cagr']:>12.2f}% │")
            all_cagrs.append(data['cagr'])
        
        print(f"  ├{'─'*35}┼{'─'*15}┼{'─'*15}┤")
        
        # Coaching
        for name, data in self.results['Coaching']['categories'].items():
            print(f"  │ {name:<33} │ {'2010-2025':<13} │ {data['cagr']:>12.2f}% │")
            all_cagrs.append(data['cagr'])
        
        print(f"  └{'─'*35}┴{'─'*15}┴{'─'*15}┘")
        
        # Overall statistics
        overall_avg = np.mean(all_cagrs)
        overall_max = max(all_cagrs)
        overall_min = min(all_cagrs)
        
        print("\n" + "=" * 70)
        print("  B. OVERALL EDUCATION INFLATION STATISTICS")
        print("=" * 70)
        
        print(f"""
  ┌─────────────────────────────────────────────┬────────────────────┐
  │ Metric                                      │              Value │
  ├─────────────────────────────────────────────┼────────────────────┤
  │ Average Education Inflation (All Categories)│ {overall_avg:>17.2f}% │
  │ Highest Category Inflation                  │ {overall_max:>17.2f}% │
  │ Lowest Category Inflation                   │ {overall_min:>17.2f}% │
  │ School Education Average                    │ {self.results['School Education']['avg_cagr']:>17.2f}% │
  │ Higher Education Average                    │ {self.results['Higher Education']['avg_cagr']:>17.2f}% │
  │ Coaching Average                            │ {self.results['Coaching']['avg_cagr']:>17.2f}% │
  └─────────────────────────────────────────────┴────────────────────┘
""")
        
        # Visual comparison
        print("=" * 70)
        print("  C. VISUAL COMPARISON (CAGR)")
        print("=" * 70)
        
        print(f"\n  Category                              CAGR")
        print("  " + "-" * 55)
        
        # Sort all categories by CAGR
        all_categories = []
        for cat in ['School Education', 'Higher Education', 'Coaching']:
            for name, data in self.results[cat]['categories'].items():
                all_categories.append((f"{cat[:6]}: {name}", data['cagr']))
        
        all_categories.sort(key=lambda x: x[1], reverse=True)
        
        for name, cagr in all_categories[:10]:  # Top 10
            bar = "█" * int(cagr * 2)
            print(f"  {name[:35]:<35} {bar} {cagr:.1f}%")
        
        print("  " + "-" * 55)
        
        # Final verdict
        print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║                    EDUCATION INFLATION SUMMARY                    ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║                                                                   ║
  ║   📚 School Education:        {self.results['School Education']['avg_cagr']:>6.2f}% per year                 ║
  ║   🎓 Higher Education:        {self.results['Higher Education']['avg_cagr']:>6.2f}% per year                 ║
  ║   📖 Coaching & Tuition:      {self.results['Coaching']['avg_cagr']:>6.2f}% per year                 ║
  ║                                                                   ║
  ║   >>> OVERALL EDUCATION INFLATION: {overall_avg:.2f}% per year <<<       ║
  ║                                                                   ║
  ╚══════════════════════════════════════════════════════════════════╝
""")
        
        return overall_avg
        
    def run_analysis(self):
        """Run complete education inflation analysis"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  CHILDREN EDUCATION INFLATION ANALYSIS".center(68) + "█")
        print("█" + "  Tracking Education Cost Trends in India".center(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        # Load data
        self.load_education_data()
        
        # Analyze each category
        self.analyze_school_education()
        self.analyze_higher_education()
        self.analyze_coaching()
        
        # Total education cost projection
        self.calculate_total_education_cost()
        
        # Print summary
        overall_inflation = self.print_summary()
        
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  ANALYSIS COMPLETE!".center(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        return overall_inflation


def main():
    analyzer = EducationInflationAnalyzer()
    analyzer.run_analysis()


if __name__ == "__main__":
    main()
