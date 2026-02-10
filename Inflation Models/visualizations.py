"""
Visualization module for inflation analysis
Creates charts and graphs for the analysis results
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np


class InflationVisualizer:
    def __init__(self):
        self.colors = {
            'gold': '#FFD700',
            'car': '#4169E1',
            'real_estate': '#228B22'
        }
        plt.style.use('seaborn-v0_8-whitegrid')
    
    def plot_inflation_comparison(self, results):
        """Create bar chart comparing inflation rates"""
        categories = []
        rates = []
        colors = []
        
        if 'gold_inflation' in results:
            categories.append('Gold')
            rates.append(results['gold_inflation']['average'])
            colors.append(self.colors['gold'])
        
        if 'car_inflation' in results:
            categories.append('Car')
            rates.append(results['car_inflation']['average'])
            colors.append(self.colors['car'])
        
        if 'real_estate_inflation' in results:
            categories.append('Real Estate')
            rates.append(results['real_estate_inflation']['average'])
            colors.append(self.colors['real_estate'])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(categories, rates, color=colors, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for bar, rate in zip(bars, rates):
            height = bar.get_height()
            ax.annotate(f'{rate:.2f}%',
                       xy=(bar.get_x() + bar.get_width() / 2, height),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom',
                       fontsize=12, fontweight='bold')
        
        ax.set_ylabel('Inflation Rate (%)', fontsize=12)
        ax.set_title('Average Inflation Rate Comparison', fontsize=14, fontweight='bold')
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        plt.savefig('inflation_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ Chart saved as 'inflation_comparison.png'")
    
    def plot_model_performance(self, model_results, dataset_name):
        """Create horizontal bar chart for model performance"""
        if model_results is None or model_results.empty:
            return
        
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Sort by R2 Score
        df = model_results.sort_values('R2_Score', ascending=True)
        
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(df)))
        
        bars = ax.barh(df['Model'], df['R2_Score'], color=colors, edgecolor='black')
        
        ax.set_xlabel('R² Score', fontsize=12)
        ax.set_title(f'Model Performance Comparison - {dataset_name}', fontsize=14, fontweight='bold')
        ax.axvline(x=0, color='black', linestyle='-', linewidth=0.5)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            ax.annotate(f'{width:.4f}',
                       xy=(width, bar.get_y() + bar.get_height() / 2),
                       xytext=(5, 0),
                       textcoords="offset points",
                       ha='left', va='center',
                       fontsize=9)
        
        plt.tight_layout()
        plt.savefig(f'model_performance_{dataset_name.lower().replace(" ", "_")}.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_price_trends(self, data, title, price_column=None):
        """Plot price trends over time"""
        if data is None or data.empty:
            return
        
        # Find price column
        if price_column is None:
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            for col in numeric_cols:
                if any(kw in col.lower() for kw in ['price', 'value', 'rate']):
                    price_column = col
                    break
            if price_column is None and len(numeric_cols) > 0:
                price_column = numeric_cols[0]
        
        if price_column is None:
            return
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        ax.plot(range(len(data)), data[price_column], 
               marker='o', linewidth=2, markersize=4,
               color='#2E86AB', label=price_column)
        
        ax.fill_between(range(len(data)), data[price_column], 
                       alpha=0.3, color='#2E86AB')
        
        ax.set_xlabel('Time Period', fontsize=12)
        ax.set_ylabel(price_column, fontsize=12)
        ax.set_title(f'{title} - Price Trend', fontsize=14, fontweight='bold')
        ax.legend()
        
        plt.tight_layout()
        plt.savefig(f'{title.lower().replace(" ", "_")}_trend.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
    
    def plot_all_trends(self, gold_data, car_data, real_estate_data):
        """Plot all three datasets in a single figure"""
        fig, axes = plt.subplots(3, 1, figsize=(14, 12))
        
        datasets = [
            (gold_data, 'Gold Prices', self.colors['gold']),
            (car_data, 'Car Prices', self.colors['car']),
            (real_estate_data, 'Real Estate Prices', self.colors['real_estate'])
        ]
        
        for ax, (data, title, color) in zip(axes, datasets):
            if data is not None and not data.empty:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    price_col = numeric_cols[0]
                    ax.plot(range(len(data)), data[price_col], 
                           marker='o', linewidth=2, markersize=3,
                           color=color, label=price_col)
                    ax.fill_between(range(len(data)), data[price_col], 
                                   alpha=0.3, color=color)
                    ax.set_title(title, fontsize=12, fontweight='bold')
                    ax.set_xlabel('Time Period')
                    ax.set_ylabel(price_col)
                    ax.legend()
        
        plt.tight_layout()
        plt.savefig('all_price_trends.png', dpi=300, bbox_inches='tight')
        plt.show()
        print("✓ Chart saved as 'all_price_trends.png'")


def main():
    """Test visualizations with sample data"""
    viz = InflationVisualizer()
    
    # Sample results for testing
    sample_results = {
        'gold_inflation': {'average': 5.2, 'overall': 12.5},
        'car_inflation': {'average': 3.8, 'overall': 8.2},
        'real_estate_inflation': {'average': 7.1, 'overall': 15.3}
    }
    
    viz.plot_inflation_comparison(sample_results)


if __name__ == "__main__":
    main()
