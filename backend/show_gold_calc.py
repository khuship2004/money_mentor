import pandas as pd
import numpy as np
from scipy import stats

excel_path = '../Inflation Models/combined_dataset_20251005_175959.xlsx'
gold_data = pd.read_excel(excel_path, sheet_name='Gold_Data')
gold_data['Date'] = pd.to_datetime(gold_data['Date'])
gold_data['Year'] = gold_data['Date'].dt.year

# Yearly aggregation
yearly = gold_data.groupby('Year')['Price'].agg(['mean', 'min', 'max', 'count']).reset_index()
yearly.columns = ['Year', 'Avg_Price', 'Min_Price', 'Max_Price', 'Data_Points']
yearly['YoY_Change'] = yearly['Avg_Price'].pct_change() * 100

print('='*80)
print('GOLD PRICE DATA & INFLATION CALCULATION')
print('='*80)

first_year = yearly['Year'].iloc[0]
last_year = yearly['Year'].iloc[-1]
first_price = yearly['Avg_Price'].iloc[0]
last_price = yearly['Avg_Price'].iloc[-1]
total_years = last_year - first_year

print(f'\nPeriod: {first_year} - {last_year} ({total_years} years)')
print(f'Total Records in Dataset: {len(gold_data)}')

print(f'\nYear    Avg Price       Min        Max      YoY %')
print('-'*55)
for _, row in yearly.iterrows():
    yoy = f'{row["YoY_Change"]:+.2f}%' if pd.notna(row['YoY_Change']) else 'N/A'
    print(f'{int(row["Year"]):<6} Rs.{row["Avg_Price"]:>10,.0f} {row["Min_Price"]:>10,.0f} {row["Max_Price"]:>10,.0f} {yoy:>10}')

# Calculations
print('\n' + '='*80)
print('INFLATION CALCULATIONS')
print('='*80)

# 1. CAGR
cagr = ((last_price / first_price) ** (1 / total_years) - 1) * 100
print(f'\n1. CAGR (Compound Annual Growth Rate):')
print(f'   Formula: ((End/Start)^(1/years) - 1) * 100')
print(f'   = (({last_price:,.0f}/{first_price:,.0f})^(1/{total_years}) - 1) * 100')
print(f'   = {cagr:.2f}%')

# 2. Geometric Mean
growth_rates = yearly['Avg_Price'] / yearly['Avg_Price'].shift(1)
growth_rates = growth_rates.dropna()
geo_mean = (np.prod(growth_rates) ** (1 / len(growth_rates)) - 1) * 100
print(f'\n2. Geometric Mean (using ALL {len(growth_rates)} year pairs):')
print(f'   = {geo_mean:.2f}%')

# 3. Linear Regression
years = yearly['Year'].values.astype(float)
prices = yearly['Avg_Price'].values.astype(float)
log_prices = np.log(prices)
slope, intercept, r_value, p_value, std_err = stats.linregress(years, log_prices)
regression_rate = (np.exp(slope) - 1) * 100
print(f'\n3. Linear Regression (on log prices):')
print(f'   Slope: {slope:.4f}')
print(f'   R-squared: {r_value**2:.4f} ({r_value**2*100:.1f}% model fit)')
print(f'   Annual Rate: (e^{slope:.4f} - 1) * 100 = {regression_rate:.2f}%')

# 4. Weighted Average
yoy_changes = yearly['Avg_Price'].pct_change().dropna() * 100
weights = np.arange(1, len(yoy_changes) + 1)
weighted_avg = np.average(yoy_changes, weights=weights)
print(f'\n4. Weighted Average (higher weight to recent years):')
print(f'   = {weighted_avg:.2f}%')

# 5. Simple Average YoY
simple_avg = yoy_changes.mean()
print(f'\n5. Simple Average YoY:')
print(f'   = {simple_avg:.2f}%')

# Best Estimate
if r_value**2 > 0.85:
    best = regression_rate * 0.4 + geo_mean * 0.3 + weighted_avg * 0.3
    print(f'\nBEST ESTIMATE (R² > 0.85):')
    print(f'   = 40% Regression + 30% Geometric + 30% Weighted')
else:
    best = geo_mean * 0.4 + weighted_avg * 0.35 + cagr * 0.25
    print(f'\nBEST ESTIMATE (R² <= 0.85):')
    print(f'   = 40% Geometric + 35% Weighted + 25% CAGR')
print(f'   = {best:.2f}%')

total_inflation = ((last_price - first_price) / first_price) * 100
print(f'\nTOTAL INFLATION ({first_year}-{last_year}): {total_inflation:.2f}%')
