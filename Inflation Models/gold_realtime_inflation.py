"""
Real-Time Gold Inflation Rate Calculator
Fetches live gold prices and calculates CAGR-based inflation rate
Updates every 30 seconds
"""

import requests
import json
from datetime import datetime
import time
import os
import sys


class RealTimeGoldInflationTracker:
    def __init__(self):
        # API Configuration - Using MetalPriceAPI
        self.api_key = "bfaae7c74636a6cea51bbf8182bee757"
        self.base_url = "https://api.metalpriceapi.com/v1"
        
        # Alternative free APIs for gold price
        self.goldapi_key = "goldapi-demo"  # Free tier
        self.goldapi_url = "https://www.goldapi.io/api/XAU/INR"
        
        # Conversion: 1 troy ounce = 31.1035 grams
        # Gold is quoted in ounces, we convert to 10 grams (standard in India)
        self.ounce_to_gram = 31.1035
        
        # Historical baseline data (from your Excel dataset)
        self.baseline = {
            'year': 2014,
            'avg_price': 28101.36,  # Average price in 2014 (Rs. per 10 grams)
            'start_date': datetime(2014, 1, 1)
        }
        
        # Current state
        self.current_price = None
        self.last_updated = None
        self.inflation_rate = None
        self.update_count = 0
        
    def fetch_gold_price_metalpriceapi(self):
        """Fetch gold price from MetalPriceAPI"""
        try:
            url = f"{self.base_url}/latest"
            params = {
                "api_key": self.api_key,
                "base": "INR",
                "currencies": "XAU"
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('success'):
                # Price is INR per 1 troy ounce of gold
                # We need to convert to INR per 10 grams
                rate_per_ounce = 1 / data['rates']['XAU']
                rate_per_gram = rate_per_ounce / self.ounce_to_gram
                rate_per_10gram = rate_per_gram * 10
                
                return rate_per_10gram
            else:
                return None
                
        except Exception as e:
            return None
    
    def fetch_gold_price_alternative(self):
        """Alternative: Fetch from GoldAPI.io"""
        try:
            headers = {
                "x-access-token": self.goldapi_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(self.goldapi_url, headers=headers, timeout=10)
            data = response.json()
            
            if 'price_gram_24k' in data:
                # Price per gram, convert to per 10 grams
                return data['price_gram_24k'] * 10
            else:
                return None
                
        except Exception as e:
            return None
    
    def fetch_gold_price_forex(self):
        """Alternative: Fetch from free forex API and convert"""
        try:
            # Using exchangerate-api for USD/INR and a gold price API
            # First get gold price in USD
            gold_usd_url = "https://api.coingecko.com/api/v3/simple/price?ids=tether-gold&vs_currencies=usd"
            response = requests.get(gold_usd_url, timeout=10)
            gold_data = response.json()
            
            if 'tether-gold' in gold_data:
                gold_usd_per_oz = gold_data['tether-gold']['usd']
                
                # Get USD to INR rate
                forex_url = "https://api.exchangerate-api.com/v4/latest/USD"
                forex_response = requests.get(forex_url, timeout=10)
                forex_data = forex_response.json()
                
                usd_to_inr = forex_data['rates']['INR']
                
                # Calculate INR per 10 grams
                gold_inr_per_oz = gold_usd_per_oz * usd_to_inr
                gold_inr_per_gram = gold_inr_per_oz / self.ounce_to_gram
                gold_inr_per_10gram = gold_inr_per_gram * 10
                
                return gold_inr_per_10gram
            
            return None
            
        except Exception as e:
            return None
    
    def fetch_gold_price_simulation(self):
        """Simulated real-time price based on last known price with small variations"""
        import random
        
        # Base price from recent data (approximately current market rate)
        base_price = 78500  # Approximate current gold price per 10 grams in INR
        
        # Add small random variation (-0.5% to +0.5%) to simulate real-time changes
        variation = random.uniform(-0.005, 0.005)
        simulated_price = base_price * (1 + variation)
        
        # Add time-based trend (slight upward during market hours)
        hour = datetime.now().hour
        if 9 <= hour <= 17:  # Market hours
            simulated_price *= 1.001  # Slight upward bias
        
        return round(simulated_price, 2)
    
    def get_current_gold_price(self):
        """Get current gold price, trying multiple sources"""
        
        # Try primary API first
        price = self.fetch_gold_price_metalpriceapi()
        source = "MetalPriceAPI"
        
        # If failed, try alternative
        if price is None:
            price = self.fetch_gold_price_alternative()
            source = "GoldAPI.io"
        
        # If still failed, try forex-based calculation
        if price is None:
            price = self.fetch_gold_price_forex()
            source = "CoinGecko + ExchangeRate"
        
        # If all APIs fail, use simulation
        if price is None:
            price = self.fetch_gold_price_simulation()
            source = "Simulated (APIs unavailable)"
        
        return price, source
    
    def calculate_cagr(self, ending_price):
        """Calculate CAGR (Compound Annual Growth Rate)"""
        starting_price = self.baseline['avg_price']
        start_date = self.baseline['start_date']
        current_date = datetime.now()
        
        # Calculate years (including partial years)
        days_elapsed = (current_date - start_date).days
        years = days_elapsed / 365.25
        
        # CAGR Formula: ((Ending/Starting)^(1/years)) - 1
        if years > 0 and starting_price > 0:
            cagr = ((ending_price / starting_price) ** (1 / years) - 1) * 100
            return cagr, years
        return 0, 0
    
    def calculate_simple_inflation(self, ending_price):
        """Calculate simple total inflation percentage"""
        starting_price = self.baseline['avg_price']
        return ((ending_price - starting_price) / starting_price) * 100
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_dashboard(self, price, source, cagr, years, total_inflation):
        """Display the real-time dashboard"""
        self.clear_screen()
        
        now = datetime.now()
        
        print("█" * 80)
        print("█" + " " * 78 + "█")
        print("█" + "  REAL-TIME GOLD INFLATION RATE CALCULATOR".center(78) + "█")
        print("█" + "  Live Price Updates Every 30 Seconds".center(78) + "█")
        print("█" + " " * 78 + "█")
        print("█" * 80)
        
        print(f"\n  Last Updated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"  Data Source: {source}")
        print(f"  Update Count: {self.update_count}")
        
        # Current Price Section
        print("\n" + "=" * 70)
        print("  CURRENT GOLD PRICE")
        print("=" * 70)
        
        print(f"""
  ┌────────────────────────────────────────────────────────────────┐
  │                                                                │
  │   LIVE GOLD PRICE (24K, 10 Grams):  Rs. {price:>12,.2f}          │
  │                                                                │
  └────────────────────────────────────────────────────────────────┘
""")
        
        # Baseline Section
        print("=" * 70)
        print("  BASELINE DATA (From Historical Dataset)")
        print("=" * 70)
        
        print(f"\n  Baseline Year:       {self.baseline['year']}")
        print(f"  Baseline Price:      Rs. {self.baseline['avg_price']:,.2f} per 10 grams")
        print(f"  Time Elapsed:        {years:.2f} years ({int(years*365.25)} days)")
        print(f"  Price Change:        Rs. {price - self.baseline['avg_price']:+,.2f}")
        
        # Inflation Calculations
        print("\n" + "=" * 70)
        print("  INFLATION CALCULATIONS")
        print("=" * 70)
        
        print(f"""
  ┌────────────────────────────────────────────┬────────────────────┐
  │ Metric                                     │              Value │
  ├────────────────────────────────────────────┼────────────────────┤
  │ Total Inflation ({self.baseline['year']} → Now)              │ {total_inflation:>17.2f}% │
  │ CAGR (Compound Annual Growth Rate)         │ {cagr:>17.2f}% │
  │ Daily Equivalent Rate                      │ {cagr/365:>17.4f}% │
  │ Monthly Equivalent Rate                    │ {cagr/12:>17.2f}% │
  └────────────────────────────────────────────┴────────────────────┘
""")
        
        # CAGR Formula Display
        print("  CAGR Formula Applied:")
        print(f"  CAGR = (Rs. {price:,.2f} / Rs. {self.baseline['avg_price']:,.2f})^(1/{years:.2f}) - 1")
        print(f"       = ({price/self.baseline['avg_price']:.4f})^({1/years:.4f}) - 1")
        print(f"       = {cagr:.2f}%")
        
        # Investment Projection
        print("\n" + "=" * 70)
        print("  INVESTMENT PROJECTION (Based on Current CAGR)")
        print("=" * 70)
        
        investment = 100000
        print(f"\n  If you invest Rs. {investment:,} today at {cagr:.2f}% CAGR:")
        
        print(f"\n  {'Years':<10} {'Projected Value':>20} {'Gain':>18}")
        print("  " + "-" * 50)
        
        for yr in [1, 3, 5, 10, 15, 20]:
            future_value = investment * ((1 + cagr/100) ** yr)
            gain = future_value - investment
            print(f"  {yr:<10} Rs. {future_value:>16,.0f} Rs. {gain:>14,.0f}")
        
        print("  " + "-" * 50)
        
        # Status indicator
        if cagr > 12:
            trend = "📈 HIGH INFLATION"
            color_indicator = "🔴"
        elif cagr > 8:
            trend = "📊 MODERATE INFLATION"
            color_indicator = "🟡"
        else:
            trend = "📉 LOW INFLATION"
            color_indicator = "🟢"
        
        print(f"\n  {color_indicator} Status: {trend} ({cagr:.2f}% CAGR)")
        
        print("\n" + "=" * 70)
        print("  Press Ctrl+C to stop the tracker")
        print("=" * 70)
        print(f"\n  ⏳ Next update in 30 seconds...")
    
    def run_tracker(self, update_interval=30):
        """Run the real-time tracker"""
        print("\n" + "█" * 60)
        print("  Starting Real-Time Gold Inflation Tracker...")
        print("  Update Interval: 30 seconds")
        print("█" * 60)
        
        try:
            while True:
                self.update_count += 1
                
                # Fetch current gold price
                price, source = self.get_current_gold_price()
                self.current_price = price
                self.last_updated = datetime.now()
                
                # Calculate CAGR and inflation
                cagr, years = self.calculate_cagr(price)
                total_inflation = self.calculate_simple_inflation(price)
                
                self.inflation_rate = cagr
                
                # Display dashboard
                self.display_dashboard(price, source, cagr, years, total_inflation)
                
                # Wait for next update
                time.sleep(update_interval)
                
        except KeyboardInterrupt:
            print("\n\n" + "=" * 60)
            print("  Tracker Stopped by User")
            print("=" * 60)
            print(f"\n  Final Statistics:")
            print(f"  - Last Price: Rs. {self.current_price:,.2f}")
            print(f"  - Last CAGR: {self.inflation_rate:.2f}%")
            print(f"  - Total Updates: {self.update_count}")
            print(f"  - Last Updated: {self.last_updated.strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n  Thank you for using the Gold Inflation Tracker!")
            print("=" * 60)


def main():
    print("\n" + "█" * 70)
    print("█" + " " * 68 + "█")
    print("█" + "  REAL-TIME GOLD INFLATION RATE CALCULATOR".center(68) + "█")
    print("█" + " " * 68 + "█")
    print("█" * 70)
    
    print("""
    This tool calculates the real-time inflation rate for gold
    using live market prices and CAGR methodology.
    
    Configuration:
    - Baseline Year: 2014
    - Baseline Price: Rs. 28,101.36 per 10 grams
    - Update Interval: 30 seconds
    - Data Source: Live API / Simulated
    
    Starting tracker in 3 seconds...
    """)
    
    time.sleep(3)
    
    tracker = RealTimeGoldInflationTracker()
    tracker.run_tracker(update_interval=30)


if __name__ == "__main__":
    main()
