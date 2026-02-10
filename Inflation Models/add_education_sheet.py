"""
Script to add Education_Data sheet to the combined Excel file
"""
import pandas as pd

excel_path = r'C:\Users\Mahina Varma\OneDrive\Desktop\BE Project Datasets\BE Project Implementation\money_mentor\src\combined_dataset_20251005_175959.xlsx'

# Create Education Data
education_data = pd.DataFrame({
    'Year': [2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 
             2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    
    'Budget_School_Annual': [15000, 16500, 18000, 20000, 22000, 25000, 28000, 32000, 36000, 40000,
                              45000, 50000, 55000, 62000, 70000, 72000, 75000, 82000, 92000, 105000, 120000],
    
    'MidRange_School_Annual': [35000, 40000, 45000, 52000, 60000, 70000, 82000, 95000, 110000, 125000,
                                145000, 165000, 185000, 210000, 240000, 250000, 265000, 295000, 330000, 375000, 425000],
    
    'Premium_School_Annual': [80000, 95000, 115000, 140000, 170000, 200000, 240000, 290000, 350000, 420000,
                               500000, 600000, 720000, 850000, 1000000, 1050000, 1150000, 1300000, 1500000, 1750000, 2000000],
    
    'Govt_College_Total': [25000, 28000, 32000, 36000, 40000, 45000, 50000, 55000, 62000, 70000,
                           80000, 90000, 100000, 115000, 130000, 140000, 155000, 175000, 200000, 225000, 250000],
    
    'Private_College_Total': [100000, 120000, 145000, 175000, 210000, 250000, 300000, 360000, 430000, 520000,
                              620000, 740000, 880000, 1050000, 1250000, 1350000, 1500000, 1700000, 1950000, 2250000, 2600000],
    
    'Engineering_Total': [150000, 180000, 220000, 270000, 330000, 400000, 480000, 580000, 700000, 850000,
                          1000000, 1200000, 1450000, 1750000, 2100000, 2300000, 2600000, 3000000, 3500000, 4100000, 4800000],
    
    'Medical_MBBS_Total': [300000, 380000, 480000, 600000, 750000, 950000, 1200000, 1500000, 1900000, 2400000,
                           3000000, 3800000, 4800000, 6000000, 7500000, 8500000, 10000000, 12000000, 15000000, 18000000, 22000000],
    
    'MBA_Total': [200000, 250000, 320000, 400000, 500000, 650000, 820000, 1000000, 1250000, 1550000,
                  1900000, 2350000, 2900000, 3500000, 4300000, 4800000, 5500000, 6500000, 7800000, 9200000, 11000000]
})

# Load existing workbook and add new sheet
with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    education_data.to_excel(writer, sheet_name='Education_Data', index=False)

print("=" * 60)
print("  Education_Data sheet added successfully!")
print("=" * 60)
print(f"\nFile: {excel_path}")
print(f"\nColumns added:")
for col in education_data.columns:
    print(f"  - {col}")
print(f"\nYears covered: {education_data['Year'].min()} - {education_data['Year'].max()}")
print(f"Total rows: {len(education_data)}")

# Verify
xl = pd.ExcelFile(excel_path)
print(f"\nAll sheets in Excel file now:")
for sheet in xl.sheet_names:
    print(f"  ✓ {sheet}")
