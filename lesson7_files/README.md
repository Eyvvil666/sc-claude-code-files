# E-commerce Business Analytics Dashboard

A comprehensive business intelligence solution featuring both Jupyter notebook analysis and a professional Streamlit dashboard for e-commerce sales data with configurable time periods and reusable business metrics calculations.

## Overview

This project transforms a basic exploratory data analysis into a professional, maintainable business intelligence framework. The refactored solution provides:

- **Configurable Analysis**: Easily analyze any time period or compare different years
- **Modular Architecture**: Reusable data loading and metrics calculation modules
- **Professional Visualizations**: Business-oriented charts with proper formatting
- **Strategic Insights**: Automated generation of business recommendations

## Project Structure

```
data_analysis/
├── EDA_Refactored.ipynb     # Main analysis notebook
├── dashboard.py             # Streamlit dashboard application
├── data_loader.py           # Data loading and processing module
├── business_metrics.py      # Business metrics calculation module
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── ecommerce_data/         # Data directory
    ├── orders_dataset.csv
    ├── order_items_dataset.csv
    ├── products_dataset.csv
    ├── customers_dataset.csv
    ├── order_reviews_dataset.csv
    └── order_payments_dataset.csv
```

## Features

### 1. Configurable Analysis Framework
- Set analysis year, comparison year, and month filters
- Flexible time period analysis without code changes
- Automatic handling of missing data periods

### 2. Comprehensive Business Metrics
- **Revenue Analysis**: Total revenue, growth rates, average order value
- **Product Performance**: Category analysis, revenue share, top performers
- **Geographic Insights**: State-level revenue and order analysis
- **Customer Satisfaction**: Review scores, satisfaction distribution
- **Delivery Performance**: Delivery times, speed categorization

### 3. Professional Visualizations
- Monthly revenue trend charts
- Product category performance bars
- Interactive geographic heatmaps
- Customer satisfaction distributions
- Consistent color schemes and formatting

### 4. Automated Insights
- Strategic recommendations based on data patterns
- Performance benchmarking and alerts
- Executive summary generation

## Installation and Setup

### Prerequisites
- Python 3.8 or higher
- Jupyter Notebook or JupyterLab (for notebook analysis)

### Installation Steps

1. **Clone or download the project files**

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure data files are in place**:
   - Place CSV files in the `ecommerce_data/` directory
   - Verify all required files are present (see Project Structure above)

4. **Run the applications**:

   **For Streamlit Dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

   **For Jupyter Notebook Analysis**:
   ```bash
   jupyter notebook EDA_Refactored.ipynb
   ```

## Usage Guide

### Streamlit Dashboard

1. **Launch the dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

2. **Navigate the interface**:
   - Use the **year filter** in the top-right to select analysis period
   - View **KPI cards** showing key metrics with trend indicators
   - Explore **interactive charts** in the 2x2 grid layout
   - Monitor **customer experience metrics** in the bottom row

3. **Dashboard Features**:
   - **Real-time filtering**: All charts update automatically when year is changed
   - **Professional styling**: Clean, business-ready interface
   - **Trend indicators**: Green/red arrows showing performance changes
   - **Formatted values**: Currency displayed as $300K, $2M for readability

### Notebook Analysis

1. **Open the refactored notebook**: `EDA_Refactored.ipynb`

2. **Configure analysis parameters** in the first code cell:
   ```python
   ANALYSIS_YEAR = 2023        # Year to analyze
   COMPARISON_YEAR = 2022      # Comparison year (optional)
   ANALYSIS_MONTH = None       # Specific month or None for full year
   DATA_PATH = 'ecommerce_data/'
   ```

3. **Run all cells** to generate the complete analysis

### Advanced Configuration

#### Analyzing Specific Time Periods
```python
# Analyze only Q4 2023
for month in [10, 11, 12]:
    ANALYSIS_MONTH = month
    # Run analysis
```

#### Custom Data Paths
```python
# Use different data location
DATA_PATH = '/path/to/your/data/'
```

#### Filtering by Order Status
```python
# Modify in data_loader.py create_sales_dataset method
status_filter = 'delivered'  # or 'shipped', 'processing', etc.
```

### Module Usage

#### Data Loading Module
```python
from data_loader import load_datasets, prepare_sales_data, add_temporal_features, filter_by_period, calculate_delivery_speed

# Load all datasets
datasets = load_datasets('ecommerce_data')

# Build and enrich the sales DataFrame
sales_df = prepare_sales_data(datasets['order_items'], datasets['orders'])
sales_df = add_temporal_features(sales_df, 'order_purchase_timestamp')

# Filter to delivered orders for a specific year (or year + month)
delivered = sales_df[sales_df['order_status'] == 'delivered'].copy()
current_df = calculate_delivery_speed(filter_by_period(delivered, 2023))
current_df_june = calculate_delivery_speed(filter_by_period(delivered, 2023, month=6))
```

#### Business Metrics Module
```python
from business_metrics import (
    calculate_revenue, calculate_avg_order_value, calculate_order_count,
    calculate_mom_growth, calculate_category_revenue,
    calculate_state_revenue, calculate_delivery_satisfaction,
)

# Revenue KPIs
revenue = calculate_revenue(current_df)
aov     = calculate_avg_order_value(current_df)
orders  = calculate_order_count(current_df)

# Month-over-month growth series
mom_growth = calculate_mom_growth(current_df)

# Category and geographic breakdowns
cat_rev   = calculate_category_revenue(current_df, datasets['products'])
state_rev = calculate_state_revenue(current_df, datasets['orders'], datasets['customers'])

# Delivery satisfaction analysis
sat_df = calculate_delivery_satisfaction(current_df, datasets['reviews'])
```

## Key Business Metrics

### Revenue Metrics
- **Total Revenue**: Sum of all delivered order item prices
- **Revenue Growth Rate**: Year-over-year percentage change
- **Average Order Value (AOV)**: Average total value per order
- **Monthly Growth Trends**: Month-over-month performance

### Product Performance
- **Category Revenue**: Revenue by product category
- **Market Share**: Percentage of total revenue by category
- **Category Diversity**: Distribution across product lines

### Geographic Analysis
- **State Performance**: Revenue and order count by state
- **Market Penetration**: Number of active markets
- **Regional AOV**: Average order value by geographic region

### Customer Experience
- **Review Scores**: Average satisfaction rating (1-5 scale)
- **Satisfaction Distribution**: Percentage of high/low ratings
- **Delivery Performance**: Average delivery time and speed metrics

## Output Examples

### Console Output
```
BUSINESS METRICS SUMMARY - 2023
============================================================

REVENUE PERFORMANCE:
  Total Revenue: $3,360,294.74
  Total Orders: 4,635
  Average Order Value: $724.98
  Revenue Growth: -2.5%

CUSTOMER SATISFACTION:
  Average Review Score: 4.10/5.0
  High Satisfaction (4+): 84.2%

DELIVERY PERFORMANCE:
  Average Delivery Time: 8.0 days
  Fast Delivery (≤3 days): 28.5%
```

### Generated Visualizations
- Monthly revenue trend line charts
- Top product category horizontal bar charts
- Interactive US state choropleth maps
- Customer satisfaction distribution charts

## Customization Options

### Adding New Metrics
1. Add a standalone function to `business_metrics.py` following the pattern `calculate_<metric>(df, ...) -> value`
2. Import the function in `dashboard.py` or the notebook and call it with the appropriate filtered DataFrame
3. Render the result in the desired KPI card or chart section

### Custom Visualizations
```python
# Example: Custom visualization
def plot_custom_metric(self, data):
    fig, ax = plt.subplots(figsize=(12, 6))
    # Your visualization code
    return fig
```

### Data Source Modifications
- Modify `data_loader.py` to handle different CSV structures
- Update column mappings in the `EcommerceDataLoader` class
- Add new data validation rules

## Troubleshooting

### Common Issues

1. **Module Import Errors**:
   - Ensure all files are in the same directory
   - Check Python path configuration

2. **Missing Data Files**:
   - Verify CSV files are in the `ecommerce_data/` directory
   - Check file naming matches expected patterns

3. **Empty Results**:
   - Verify date filters match available data
   - Check order status filtering

4. **Visualization Issues**:
   - Ensure all required packages are installed
   - Check Plotly version compatibility for interactive maps

### Performance Optimization
- For large datasets, consider chunked processing
- Use data sampling for initial exploration
- Implement caching for repeated analysis

## Dashboard Features

### Layout Structure
- **Header**: Title with year selection filter (applies globally)
- **KPI Row**: 4 metric cards with trend indicators
  - Total Revenue, Monthly Growth, Average Order Value, Total Orders
  - Color-coded trends (green for positive, red for negative)
- **Charts Grid**: 2x2 interactive visualization layout
  - Revenue trend (current vs previous year)
  - Top 10 product categories bar chart
  - US state choropleth map
  - Customer satisfaction vs delivery time analysis
- **Bottom Row**: Customer experience metrics
  - Average delivery time with trend
  - Review score with star rating

### Technical Features
- **Real-time Filtering**: All visualizations update automatically
- **Professional Styling**: Business-ready interface with uniform card heights
- **Plotly Charts**: Interactive, publication-quality visualizations
- **Responsive Design**: Adapts to different screen sizes
- **Error Handling**: Graceful handling of missing data

## Future Enhancements

### Planned Features
- Real-time data connections
- Predictive analytics and forecasting
- Customer segmentation analysis
- A/B testing framework
- Automated report scheduling
- Export functionality (PDF reports)

### Extension Ideas
- Integration with business intelligence tools
- API endpoints for metrics access
- Machine learning model integration
- Advanced statistical analysis
- Mobile-responsive improvements

## Contributing

To extend this analysis framework:

1. Follow the existing code structure and documentation patterns
2. Add comprehensive docstrings to new functions
3. Include unit tests for new business logic
4. Update this README with new features

## License

This project is provided as-is for educational and business analysis purposes.

---

**Note**: This framework is designed to be easily maintained and extended for ongoing business intelligence needs. The modular architecture ensures that updates to data sources or metric calculations can be made without affecting the overall analysis structure.