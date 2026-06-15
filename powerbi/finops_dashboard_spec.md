# Power BI Executive Dashboard Build Spec

Source file: `data/processed/finops_kpis_athena.csv`

## Import
1. Open Power BI Desktop.
2. Select Get data > Text/CSV.
3. Choose `data/processed/finops_kpis_athena.csv` and load it as table `finops_kpis_athena`.
4. In Power Query, set numeric columns to Decimal number / Whole number as appropriate.
5. Add a month date column with `Date.FromText([year_month] & "-01")` and name it `month_date`.
6. Import `powerbi/finops_exec_theme.json` from View > Themes > Browse for themes.

## Recommended Cards
- Total Net Cost: $408.0K
- Total Forecast: $1.6M
- Total Budget: $2.0B
- Budget Utilization: 0.02%
- Forecast Utilization: 25.0%
- Anomaly Count: 0

## Page 1: Executive Dashboard
- KPI cards: Total Net Cost, Forecast Utilization %, Budget Utilization %, MoM Trend, Top Provider, Anomaly Count.
- Line chart: `year_month` by Total Net Cost and Total Forecast.
- Clustered column chart: Total Net Cost by `cloud_provider`.
- Stacked column chart: `year_month` by Total Net Cost, legend `environment`.
- Bar chart: Total Net Cost by `account_id`, Top N = 8.
- Bar chart: environment mix as share of Total Net Cost.

## Page 2: Cost Drivers and Controls
- 100% stacked bar: cloud provider by environment.
- Column chart: Forecast Variance by month.
- Bar chart: Top account share of net cost.
- Line chart: monthly net cost by provider.
- Text box: executive actions from README.

## Measures
Use the measures in `powerbi/finops_dashboard_measures.dax`.
