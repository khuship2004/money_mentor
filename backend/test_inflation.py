"""Test the inflation models"""
from inflation_models import InflationRatesProvider

p = InflationRatesProvider()

print("=" * 60)
print("TESTING INFLATION MODELS - ALL CALCULATION METHODS")
print("=" * 60)

for category in ['gold', 'house', 'car', 'education']:
    data = p.get_inflation_rate(category)
    print(f"\n=== {category.upper()} ===")
    print(f"  CAGR:           {data.get('cagr', 'N/A')}%")
    print(f"  Geometric Mean: {data.get('geometric_mean', 'N/A')}%")
    print(f"  Regression:     {data.get('regression_rate', 'N/A')}% (R²: {data.get('regression_r_squared', 'N/A')})")
    print(f"  Weighted Avg:   {data.get('weighted_average', 'N/A')}%")
    print(f"  BEST ESTIMATE:  {data.get('best_estimate', data.get('cagr', 'N/A'))}%")
    print(f"  Data Points:    {data.get('data_points_used', 'N/A')}")
    print(f"  Period:         {data.get('period', 'N/A')}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
