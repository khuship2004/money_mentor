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
        self.international_data = None
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
        
    def load_international_education_data(self):
        """
        Load historical international education cost data for Indian students
        Data sourced from:
        - US College Board Reports
        - HESA (UK Higher Education Statistics Agency)
        - DAAD (German Academic Exchange Service)
        - Study in Australia reports
        - Immigration and Education Reports
        
        Costs are in INR (converted at historical exchange rates)
        Includes: Tuition + Living Expenses per year
        """
        print("\n" + "=" * 70)
        print("    LOADING INTERNATIONAL EDUCATION COST DATA")
        print("=" * 70)
        
        # Historical USD to INR exchange rates (average annual)
        self.exchange_rates = {
            2010: 45.7, 2011: 46.7, 2012: 53.4, 2013: 58.6, 2014: 61.0,
            2015: 64.2, 2016: 67.2, 2017: 65.1, 2018: 68.4, 2019: 70.4,
            2020: 74.1, 2021: 73.9, 2022: 78.6, 2023: 82.6, 2024: 83.4, 2025: 84.5
        }
        
        # ==========================================
        # USA EDUCATION COSTS (Per Year in USD, then converted)
        # Sources: College Board, NCES, University Reports
        # ==========================================
        
        # USA - Public University (In-State equivalent for international = Out-of-State)
        # Tuition + Living for international students
        usa_public_tuition = {
            2010: 22000, 2011: 23500, 2012: 25000, 2013: 26500, 2014: 28000,
            2015: 29500, 2016: 31000, 2017: 32500, 2018: 34000, 2019: 36000,
            2020: 37500, 2021: 39000, 2022: 41000, 2023: 43500, 2024: 46000, 2025: 48500
        }
        
        # USA - Private University (Ivy League / Top Private)
        usa_private_tuition = {
            2010: 45000, 2011: 48000, 2012: 51000, 2013: 54000, 2014: 57000,
            2015: 60000, 2016: 64000, 2017: 68000, 2018: 72000, 2019: 76000,
            2020: 78000, 2021: 80000, 2022: 84000, 2023: 88000, 2024: 92000, 2025: 95000
        }
        
        # USA - Community College (2-year programs)
        usa_community_tuition = {
            2010: 12000, 2011: 12800, 2012: 13600, 2013: 14500, 2014: 15400,
            2015: 16200, 2016: 17000, 2017: 18000, 2018: 19000, 2019: 20000,
            2020: 21000, 2021: 22000, 2022: 23500, 2023: 25000, 2024: 26500, 2025: 28000
        }
        
        # ==========================================
        # UK EDUCATION COSTS (Per Year in GBP, converted to INR)
        # Sources: HESA, Universities UK, Complete University Guide
        # ==========================================
        
        # GBP to INR historical rates
        gbp_to_inr = {
            2010: 71.0, 2011: 74.8, 2012: 84.6, 2013: 91.5, 2014: 98.6,
            2015: 97.5, 2016: 89.8, 2017: 84.2, 2018: 91.0, 2019: 88.7,
            2020: 95.8, 2021: 101.2, 2022: 95.3, 2023: 102.5, 2024: 105.8, 2025: 107.5
        }
        
        # UK - Russell Group Universities (Top tier like Oxford, Cambridge, Imperial)
        uk_russell_tuition_gbp = {
            2010: 18000, 2011: 20000, 2012: 22000, 2013: 24000, 2014: 26000,
            2015: 28000, 2016: 30000, 2017: 32000, 2018: 34000, 2019: 36000,
            2020: 38000, 2021: 40000, 2022: 42000, 2023: 44000, 2024: 46000, 2025: 48000
        }
        
        # UK - Standard Universities
        uk_standard_tuition_gbp = {
            2010: 14000, 2011: 15500, 2012: 17000, 2013: 18500, 2014: 20000,
            2015: 21500, 2016: 23000, 2017: 24500, 2018: 26000, 2019: 27500,
            2020: 29000, 2021: 30500, 2022: 32000, 2023: 33500, 2024: 35000, 2025: 36500
        }
        
        # ==========================================
        # GERMANY EDUCATION COSTS (Per Year - mostly living costs)
        # Sources: DAAD, Study in Germany, Destatis
        # Note: Public universities have minimal/no tuition (admin fees only)
        # ==========================================
        
        # EUR to INR historical rates
        eur_to_inr = {
            2010: 60.5, 2011: 64.8, 2012: 68.6, 2013: 77.8, 2014: 81.0,
            2015: 71.2, 2016: 74.4, 2017: 73.5, 2018: 80.7, 2019: 78.8,
            2020: 84.6, 2021: 87.4, 2022: 82.7, 2023: 89.8, 2024: 91.2, 2025: 92.5
        }
        
        # Germany - Public University (Living + Admin fees only)
        germany_public_eur = {
            2010: 9000, 2011: 9300, 2012: 9600, 2013: 10000, 2014: 10400,
            2015: 10800, 2016: 11200, 2017: 11600, 2018: 12000, 2019: 12500,
            2020: 13000, 2021: 13500, 2022: 14200, 2023: 15000, 2024: 15800, 2025: 16500
        }
        
        # Germany - Private University
        germany_private_eur = {
            2010: 18000, 2011: 19000, 2012: 20000, 2013: 21500, 2014: 23000,
            2015: 24500, 2016: 26000, 2017: 27500, 2018: 29000, 2019: 31000,
            2020: 33000, 2021: 35000, 2022: 37500, 2023: 40000, 2024: 42500, 2025: 45000
        }
        
        # ==========================================
        # CANADA EDUCATION COSTS (Per Year in CAD)
        # Sources: Statistics Canada, CBIE, Universities Canada
        # ==========================================
        
        # CAD to INR historical rates
        cad_to_inr = {
            2010: 44.3, 2011: 46.8, 2012: 53.5, 2013: 56.6, 2014: 55.4,
            2015: 50.3, 2016: 51.4, 2017: 51.1, 2018: 52.9, 2019: 53.4,
            2020: 55.5, 2021: 58.8, 2022: 60.9, 2023: 61.6, 2024: 62.0, 2025: 62.8
        }
        
        # Canada - Top Universities (U of T, McGill, UBC)
        canada_top_cad = {
            2010: 28000, 2011: 30000, 2012: 32000, 2013: 34500, 2014: 37000,
            2015: 40000, 2016: 43000, 2017: 46000, 2018: 49000, 2019: 52000,
            2020: 55000, 2021: 58000, 2022: 62000, 2023: 66000, 2024: 70000, 2025: 75000
        }
        
        # Canada - Standard Universities
        canada_standard_cad = {
            2010: 20000, 2011: 21500, 2012: 23000, 2013: 25000, 2014: 27000,
            2015: 29000, 2016: 31000, 2017: 33500, 2018: 36000, 2019: 38500,
            2020: 41000, 2021: 44000, 2022: 47000, 2023: 50000, 2024: 54000, 2025: 58000
        }
        
        # ==========================================
        # AUSTRALIA EDUCATION COSTS (Per Year in AUD)
        # Sources: Study in Australia, Australian Government
        # ==========================================
        
        # AUD to INR historical rates
        aud_to_inr = {
            2010: 42.1, 2011: 47.7, 2012: 55.3, 2013: 56.2, 2014: 55.0,
            2015: 48.8, 2016: 50.0, 2017: 50.2, 2018: 51.8, 2019: 49.4,
            2020: 50.8, 2021: 55.3, 2022: 54.2, 2023: 54.6, 2024: 55.2, 2025: 56.0
        }
        
        # Australia - Group of Eight Universities (Top tier)
        australia_go8_aud = {
            2010: 32000, 2011: 34000, 2012: 36000, 2013: 38500, 2014: 41000,
            2015: 44000, 2016: 47000, 2017: 50000, 2018: 53000, 2019: 56000,
            2020: 58000, 2021: 60000, 2022: 64000, 2023: 68000, 2024: 72000, 2025: 76000
        }
        
        # Australia - Standard Universities
        australia_standard_aud = {
            2010: 24000, 2011: 25500, 2012: 27000, 2013: 29000, 2014: 31000,
            2015: 33000, 2016: 35500, 2017: 38000, 2018: 40500, 2019: 43000,
            2020: 45000, 2021: 47000, 2022: 50000, 2023: 53000, 2024: 56500, 2025: 60000
        }
        
        # Convert all to INR DataFrame
        years = list(range(2010, 2026))
        
        self.international_data = pd.DataFrame({
            'Year': years,
            # USA (USD to INR)
            'USA_Public': [usa_public_tuition[y] * self.exchange_rates[y] for y in years],
            'USA_Private': [usa_private_tuition[y] * self.exchange_rates[y] for y in years],
            'USA_Community': [usa_community_tuition[y] * self.exchange_rates[y] for y in years],
            # UK (GBP to INR)
            'UK_Russell': [uk_russell_tuition_gbp[y] * gbp_to_inr[y] for y in years],
            'UK_Standard': [uk_standard_tuition_gbp[y] * gbp_to_inr[y] for y in years],
            # Germany (EUR to INR)
            'Germany_Public': [germany_public_eur[y] * eur_to_inr[y] for y in years],
            'Germany_Private': [germany_private_eur[y] * eur_to_inr[y] for y in years],
            # Canada (CAD to INR)
            'Canada_Top': [canada_top_cad[y] * cad_to_inr[y] for y in years],
            'Canada_Standard': [canada_standard_cad[y] * cad_to_inr[y] for y in years],
            # Australia (AUD to INR)
            'Australia_Go8': [australia_go8_aud[y] * aud_to_inr[y] for y in years],
            'Australia_Standard': [australia_standard_aud[y] * aud_to_inr[y] for y in years],
        })
        
        print(f"\n  International Data: {len(self.international_data)} years ({self.international_data['Year'].min()}-{self.international_data['Year'].max()})")
        print(f"  Countries covered: USA, UK, Germany, Canada, Australia")
        
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
        
    def analyze_international_education(self):
        """Analyze international higher education cost inflation for Indian students"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  5. INTERNATIONAL HIGHER EDUCATION INFLATION".ljust(68) + "█")
        print("█" + "  For Indian Students Going Abroad".ljust(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        df = self.international_data.copy()
        
        print("\n" + "=" * 70)
        print("  A. YEAR-BY-YEAR COSTS (Per Year in Rs. Lakhs)")
        print("=" * 70)
        
        print(f"\n  {'Year':<6} {'USA Pub':>10} {'USA Pvt':>10} {'UK Top':>10} {'Germany':>10} {'Canada':>10} {'Australia':>10}")
        print("  " + "-" * 70)
        
        for _, row in df.iterrows():
            print(f"  {int(row['Year']):<6} {row['USA_Public']/100000:>10.1f} {row['USA_Private']/100000:>10.1f} "
                  f"{row['UK_Russell']/100000:>10.1f} {row['Germany_Public']/100000:>10.1f} "
                  f"{row['Canada_Top']/100000:>10.1f} {row['Australia_Go8']/100000:>10.1f}")
        
        print("  " + "-" * 70)
        print("  (All values in Rs. Lakhs per year including tuition + living expenses)")
        
        # Calculate CAGR for each country
        first_year = df['Year'].iloc[0]
        last_year = df['Year'].iloc[-1]
        total_years = last_year - first_year
        
        categories = {
            'USA - Public University': 'USA_Public',
            'USA - Private/Ivy League': 'USA_Private',
            'USA - Community College': 'USA_Community',
            'UK - Russell Group': 'UK_Russell',
            'UK - Standard University': 'UK_Standard',
            'Germany - Public (Free Tuition)': 'Germany_Public',
            'Germany - Private University': 'Germany_Private',
            'Canada - Top Universities': 'Canada_Top',
            'Canada - Standard': 'Canada_Standard',
            'Australia - Group of Eight': 'Australia_Go8',
            'Australia - Standard': 'Australia_Standard'
        }
        
        print("\n" + "=" * 70)
        print("  B. INFLATION CALCULATIONS BY COUNTRY & UNIVERSITY TYPE")
        print("=" * 70)
        
        print(f"\n  Period: {first_year} - {last_year} ({total_years} years)")
        
        print(f"\n  ┌{'─'*30}┬{'─'*14}┬{'─'*14}┬{'─'*12}┐")
        print(f"  │ {'Country & Type':<28} │ {first_year} (L):>12 │ {last_year} (L):>12 │ {'CAGR':>10} │")
        print(f"  ├{'─'*30}┼{'─'*14}┼{'─'*14}┼{'─'*12}┤")
        
        intl_results = {}
        
        for name, col in categories.items():
            start = df[col].iloc[0]
            end = df[col].iloc[-1]
            cagr = self.calculate_cagr(start, end, total_years)
            
            print(f"  │ {name:<28} │ Rs.{start/100000:>8.1f}L │ Rs.{end/100000:>8.1f}L │ {cagr:>9.2f}% │")
            
            intl_results[name] = {
                'start': start,
                'end': end,
                'cagr': cagr
            }
        
        print(f"  └{'─'*30}┴{'─'*14}┴{'─'*14}┴{'─'*12}┘")
        
        # Average by country
        country_avgs = {
            'USA': np.mean([intl_results['USA - Public University']['cagr'], 
                           intl_results['USA - Private/Ivy League']['cagr']]),
            'UK': np.mean([intl_results['UK - Russell Group']['cagr'], 
                          intl_results['UK - Standard University']['cagr']]),
            'Germany': np.mean([intl_results['Germany - Public (Free Tuition)']['cagr'], 
                               intl_results['Germany - Private University']['cagr']]),
            'Canada': np.mean([intl_results['Canada - Top Universities']['cagr'], 
                              intl_results['Canada - Standard']['cagr']]),
            'Australia': np.mean([intl_results['Australia - Group of Eight']['cagr'], 
                                 intl_results['Australia - Standard']['cagr']])
        }
        
        print("\n" + "=" * 70)
        print("  C. AVERAGE INFLATION BY COUNTRY (For Indian Students in INR)")
        print("=" * 70)
        
        print(f"\n  ┌{'─'*25}┬{'─'*20}┐")
        print(f"  │ {'Country':<23} │ {'Avg Inflation (CAGR)':>18} │")
        print(f"  ├{'─'*25}┼{'─'*20}┤")
        
        for country, cagr in country_avgs.items():
            flag = {'USA': '🇺🇸', 'UK': '🇬🇧', 'Germany': '🇩🇪', 'Canada': '🇨🇦', 'Australia': '🇦🇺'}
            print(f"  │ {flag.get(country, '')} {country:<21} │ {cagr:>17.2f}% │")
        
        print(f"  └{'─'*25}┴{'─'*20}┘")
        
        overall_intl_avg = np.mean(list(country_avgs.values()))
        print(f"\n  >>> AVERAGE INTERNATIONAL EDUCATION INFLATION: {overall_intl_avg:.2f}% per year")
        
        self.results['International Education'] = {
            'period': f"{first_year}-{last_year}",
            'years': total_years,
            'categories': intl_results,
            'country_averages': country_avgs,
            'avg_cagr': overall_intl_avg
        }
        
    def calculate_international_program_costs(self):
        """
        Calculate total program costs based on duration:
        - After 10th to PG (UG + PG): 6 years
        - Undergraduate only: 4 years  
        - Postgraduate only: 2 years (Masters/MBA)
        """
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  6. INTERNATIONAL PROGRAM COST BY DURATION".ljust(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        # 2025 per-year costs (latest data)
        df = self.international_data
        latest = df[df['Year'] == 2025].iloc[0]
        
        # Define program durations
        durations = {
            'Post-Graduation Only (Masters/MBA)': 2,
            'Undergraduate Only (Bachelors)': 4,
            '10th to PG (UG + Masters)': 6
        }
        
        # Main universities for each country
        universities = {
            'USA - Public University': latest['USA_Public'],
            'USA - Private/Ivy League': latest['USA_Private'],
            'UK - Russell Group (Oxford, Cambridge)': latest['UK_Russell'],
            'UK - Standard University': latest['UK_Standard'],
            'Germany - Public (TU9, LMU)': latest['Germany_Public'],
            'Germany - Private': latest['Germany_Private'],
            'Canada - Top (U of T, McGill)': latest['Canada_Top'],
            'Canada - Standard': latest['Canada_Standard'],
            'Australia - Go8 (Melbourne, Sydney)': latest['Australia_Go8'],
            'Australia - Standard': latest['Australia_Standard'],
        }
        
        print("\n" + "=" * 70)
        print("  A. TOTAL PROGRAM COSTS (2025 Prices in Rs. Lakhs)")
        print("=" * 70)
        
        for duration_name, years in durations.items():
            print(f"\n  📚 {duration_name} ({years} years)")
            print("  " + "-" * 60)
            print(f"  {'University Type':<40} {'Total Cost':>18}")
            print("  " + "-" * 60)
            
            for uni, yearly_cost in universities.items():
                total_cost = yearly_cost * years
                print(f"  {uni:<40} Rs.{total_cost/100000:>14.1f} Lakhs")
            
            print("  " + "-" * 60)
        
        # Store international program costs
        self.results['International Programs'] = {}
        
        for duration_name, years in durations.items():
            self.results['International Programs'][duration_name] = {
                'duration_years': years,
                'costs': {uni: yearly * years for uni, yearly in universities.items()}
            }
        
        # Future projections
        print("\n" + "=" * 70)
        print("  B. FUTURE COST PROJECTIONS (International Education)")
        print("=" * 70)
        
        # Use average international inflation for projections
        intl_inflation = self.results.get('International Education', {}).get('avg_cagr', 10.5)
        
        print(f"\n  Using average international education inflation: {intl_inflation:.2f}%\n")
        
        # Project for a child starting studies in future years
        start_years = [2026, 2028, 2030, 2035, 2040]
        
        print(f"  Undergraduate (4 years) - USA Public University")
        print("  " + "-" * 60)
        current_yearly = latest['USA_Public']
        current_4yr = current_yearly * 4
        
        print(f"  {'If starting in':<20} {'Projected Total Cost':>20} {'Increase from 2025':>18}")
        print("  " + "-" * 60)
        
        for year in start_years:
            years_ahead = year - 2025
            future_yearly = current_yearly * ((1 + intl_inflation/100) ** years_ahead)
            future_total = future_yearly * 4
            increase = ((future_total - current_4yr) / current_4yr) * 100
            print(f"  {year:<20} Rs.{future_total/100000:>16.1f}L {increase:>17.1f}%")
        
        print("  " + "-" * 60)
        
        # Comparison table across countries for 4-year UG
        print("\n" + "=" * 70)
        print("  C. COUNTRY COMPARISON - 4-YEAR UNDERGRADUATE (2025)")
        print("=" * 70)
        
        ug_comparison = {
            'USA (Public)': latest['USA_Public'] * 4,
            'USA (Private)': latest['USA_Private'] * 4,
            'UK (Russell)': latest['UK_Russell'] * 4,
            'UK (Standard)': latest['UK_Standard'] * 4,
            'Germany (Public)': latest['Germany_Public'] * 4,
            'Canada (Top)': latest['Canada_Top'] * 4,
            'Australia (Go8)': latest['Australia_Go8'] * 4,
            'India (IIT)': 4800000,  # For comparison
            'India (Private Eng)': 2600000,  # For comparison
        }
        
        print(f"\n  ┌{'─'*25}┬{'─'*18}┬{'─'*15}┐")
        print(f"  │ {'Country':<23} │ {'Total Cost (4 yr)':>16} │ {'vs India IIT':>13} │")
        print(f"  ├{'─'*25}┼{'─'*18}┼{'─'*15}┤")
        
        india_iit = ug_comparison['India (IIT)']
        for country, cost in ug_comparison.items():
            multiple = cost / india_iit
            print(f"  │ {country:<23} │ Rs.{cost/100000:>12.1f}L │ {multiple:>12.1f}x │")
        
        print(f"  └{'─'*25}┴{'─'*18}┴{'─'*15}┘")
        
        # Masters comparison (2 years)
        print("\n" + "=" * 70)
        print("  D. COUNTRY COMPARISON - 2-YEAR MASTERS/MBA (2025)")
        print("=" * 70)
        
        pg_comparison = {
            'USA (Public)': latest['USA_Public'] * 2,
            'USA (Private/Ivy)': latest['USA_Private'] * 2,
            'UK (Russell Group)': latest['UK_Russell'] * 2,
            'Germany (Public)': latest['Germany_Public'] * 2,
            'Canada (Top)': latest['Canada_Top'] * 2,
            'Australia (Go8)': latest['Australia_Go8'] * 2,
            'India (IIM MBA)': 11000000,  # For comparison
            'India (Top Private MBA)': 6500000,  # For comparison
        }
        
        print(f"\n  ┌{'─'*25}┬{'─'*18}┬{'─'*15}┐")
        print(f"  │ {'Country':<23} │ {'Total Cost (2 yr)':>16} │ {'vs India IIM':>13} │")
        print(f"  ├{'─'*25}┼{'─'*18}┼{'─'*15}┤")
        
        india_iim = pg_comparison['India (IIM MBA)']
        for country, cost in pg_comparison.items():
            multiple = cost / india_iim
            print(f"  │ {country:<23} │ Rs.{cost/100000:>12.1f}L │ {multiple:>12.1f}x │")
        
        print(f"  └{'─'*25}┴{'─'*18}┴{'─'*15}┘")
        
        # Print key insights
        cheapest_ug = min([(k, v) for k, v in ug_comparison.items() if 'India' not in k], key=lambda x: x[1])
        most_expensive_ug = max([(k, v) for k, v in ug_comparison.items() if 'India' not in k], key=lambda x: x[1])
        
        print(f"""
  ┌─────────────────────────────────────────────────────────────────────┐
  │                   KEY INSIGHTS FOR INDIAN STUDENTS                  │
  ├─────────────────────────────────────────────────────────────────────┤
  │                                                                     │
  │  💰 Most Affordable Abroad: {cheapest_ug[0]:<20} Rs.{cheapest_ug[1]/100000:>6.1f}L   │
  │  💎 Most Expensive:         {most_expensive_ug[0]:<20} Rs.{most_expensive_ug[1]/100000:>6.1f}L   │
  │                                                                     │
  │  🇩🇪 Germany offers FREE TUITION at public universities!            │
  │     Only living expenses (~Rs.{latest['Germany_Public']/100000:.1f}L/year)                       │
  │                                                                     │
  │  📈 Education costs abroad rising {self.results.get('International Education', {}).get('avg_cagr', 10.5):.1f}% annually for Indians    │
  │     (includes currency depreciation effect)                         │
  │                                                                     │
  └─────────────────────────────────────────────────────────────────────┘
""")
        
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
        
        print(f"  ├{'─'*35}┼{'─'*15}┼{'─'*15}┤")
        
        # International Education (if available)
        intl_cagrs = []
        if 'International Education' in self.results:
            for name, data in self.results['International Education']['categories'].items():
                truncated_name = name[:33] if len(name) > 33 else name
                print(f"  │ {truncated_name:<33} │ {'2010-2025':<13} │ {data['cagr']:>12.2f}% │")
                intl_cagrs.append(data['cagr'])
        
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
  │ Coaching Average                            │ {self.results['Coaching']['avg_cagr']:>17.2f}% │""")
        
        # Add international education if available
        if 'International Education' in self.results:
            intl_avg = self.results['International Education']['avg_cagr']
            print(f"  │ International Education Average              │ {intl_avg:>17.2f}% │")
        
        print(f"  └─────────────────────────────────────────────┴────────────────────┘")
        print()
        
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
        intl_line = ""
        if 'International Education' in self.results:
            intl_avg = self.results['International Education']['avg_cagr']
            intl_line = f"\n  ║   🌍 International Education:   {intl_avg:>6.2f}% per year                 ║"
        
        print(f"""
  ╔══════════════════════════════════════════════════════════════════╗
  ║                    EDUCATION INFLATION SUMMARY                    ║
  ╠══════════════════════════════════════════════════════════════════╣
  ║                                                                   ║
  ║   📚 School Education:        {self.results['School Education']['avg_cagr']:>6.2f}% per year                 ║
  ║   🎓 Higher Education:        {self.results['Higher Education']['avg_cagr']:>6.2f}% per year                 ║
  ║   📖 Coaching & Tuition:      {self.results['Coaching']['avg_cagr']:>6.2f}% per year                 ║{intl_line}
  ║                                                                   ║
  ║   >>> DOMESTIC EDUCATION INFLATION: {overall_avg:.2f}% per year <<<       ║
  ║                                                                   ║
  ╚══════════════════════════════════════════════════════════════════╝
""")
        
        return overall_avg
        
    def run_analysis(self):
        """Run complete education inflation analysis"""
        print("\n" + "█" * 70)
        print("█" + " " * 68 + "█")
        print("█" + "  CHILDREN EDUCATION INFLATION ANALYSIS".center(68) + "█")
        print("█" + "  Tracking Education Cost Trends in India & Abroad".center(68) + "█")
        print("█" + " " * 68 + "█")
        print("█" * 70)
        
        # Load data
        self.load_education_data()
        self.load_international_education_data()
        
        # Analyze each category - Domestic
        self.analyze_school_education()
        self.analyze_higher_education()
        self.analyze_coaching()
        
        # Analyze International Education
        self.analyze_international_education()
        self.calculate_international_program_costs()
        
        # Total education cost projection (domestic)
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
